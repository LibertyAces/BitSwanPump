import logging

from ..abc.source import TriggerSource

L = logging.getLogger(__name__)


class ElasticSearchSource(TriggerSource):
	ConfigDefaults = {
		'index': 'index-*',
		'scroll_timeout': '1m',
		'source': '_source',
		'sort_by': '_id',
		# Start getting the documents from the given time
		'timestamp': '@timestamp',
		'start_from': 'now-1h',
	}

	def __init__(self, app, pipeline, connection, request_body=None, paging=True, id=None, config=None):
		"""

		**Parameters**

		app : Application
				Name of the `Application <https://asab.readthedocs.io/en/latest/asab/application.html>`_.

		pipeline : Pipeline
				Name of the Pipeline.

		connection : Connection
				Information of the connection.

		request_body JSON, default = None
				Request body needed for the request API call.

		paging : ?, default = True

		id : ID, default = None
				ID

		config : JSON/dict, default = None
				Configuration file with additional information.

		"""
		super().__init__(app, pipeline, id=id, config=config)
		self.Connection = pipeline.locate_connection(app, connection)

		self.Index = self.Config['index']
		self.ScrollTimeout = self.Config['scroll_timeout']
		self.Source = self.Config['source']
		self.SortBy = self.Config['sort_by']
		self.Paging = paging

		if request_body is not None:
			self.RequestBody = request_body

		elif len(self.Config["timestamp"]) > 0:
			self.RequestBody = {
				'query': {
					'bool': {
						'filter': [
							{
								'range': {
									self.Config['timestamp']: {
										'gte': self.Config['start_from']
									}
								}
							}
						]
					}
				}
			}

		else:
			self.RequestBody = {
				'query': {
					'bool': {
						'must': {
							'match_all': {}
						}
					}
				}}

	async def cycle(self):
		"""
		Gets data from Elastic and injects them into the pipeline.

		"""
		last_hit_sort = None
		request_body = self.RequestBody

		while True:
			path = '{}/_search'.format(self.Index)

			if last_hit_sort:
				request_body['search_after'] = last_hit_sort

			# https://www.elastic.co/guide/en/elasticsearch/reference/current/paginate-search-results.html#search-after
			if 'sort' not in request_body:
				request_body['sort'] = [{self.SortBy: 'asc'}]  # Always need a consistent sort order for deep pagination

			url = self.Connection.get_url() + path

			async with self.Connection.get_session() as session:
				async with session.post(
					url=url,
					json=request_body,
					headers=self.Connection.Headers,
					ssl=self.Connection.SSLContext,
				) as response:

					if response.status != 200:
						data = await response.text()
						L.error("Failed to fetch data from ElasticSearch: {} from {}\n{}".format(response.status, url, data))
						break

					msg = await response.json()

			hits = msg["hits"]["hits"]
			last_hit = hits[-1] if hits else None
			last_hit_sort = last_hit['sort'] if last_hit else None

			if len(hits) == 0:
				break

			# Feed messages into a pipeline
			for hit in hits:

				if self.Source not in hit:
					continue

				source = hit[self.Source]

				# Is there some additional nested info?
				if "inner_hits" in hit:

					try:
						for inner_hit in hit["inner_hits"]["hits"]["hits"]:

							if self.Source not in inner_hit:
								continue

							source.update(inner_hit[self.Source])

					except KeyError:
						pass

				await self.process(hit[self.Source])

			if not self.Paging:
				break


class ElasticSearchAggsSource(TriggerSource):
	ConfigDefaults = {
		'index': 'index-*',
	}

	def __init__(self, app, pipeline, connection, request_body=None, id=None, config=None):
		"""
		Description:

		**Parameters**

		app : Application
				Name of the `Application <https://asab.readthedocs.io/en/latest/asab/application.html>`_.

		pipeline : Pipeline
				Name of the Pipeline.

		connection : Connection
				Information of the connection.

		request_body JSON, default = None
				Request body needed for the request API call.

		id : ID, default = None
				ID info

		config : JSON/dict, default = None
				configuration file with additional information.

		"""
		super().__init__(app, pipeline, id=id, config=config)
		self.Connection = pipeline.locate_connection(app, connection)

		self.Index = self.Config['index']

		if request_body is not None:
			self.RequestBody = request_body
		else:
			self.RequestBody = {
				'query': {
					'bool': {
						'must': {
							'match_all': {}
						}
					}
				}
			}

	async def cycle(self):
		"""
		Sets request body and path to create query call.

		|

		"""
		request_body = self.RequestBody
		path = '{}/_search?'.format(self.Index)

		url = self.Connection.get_url() + path

		async with self.Connection.get_session() as session:
			async with session.post(
				url=url,
				json=request_body,
				headers=self.Connection.Headers,
				ssl=self.Connection.SSLContext,
			) as response:

				if response.status != 200:
					data = await response.text()
					L.error("Failed to fetch data from ElasticSearch: {} from {}\n{}".format(response.status, url, data))
					return

				msg = await response.json()

		aggs = msg['aggregations']

		if len(aggs) == 0:
			return

		start_name = list(aggs.keys())[0]
		start = aggs[start_name]

		path = {}
		await self.process_aggs(path, start_name, start)

	async def process_aggs(self, path, aggs_name, aggs):
		"""
		Description:

		**Parameters**

		path :

		aggs_name :

		agss :

		"""
		if 'buckets' in aggs:
			await self.process_buckets(path, aggs_name, aggs["buckets"])

		if 'value' in aggs:
			path[aggs_name] = aggs['value']

			event = {}
			event.update(path)
			await self.process(event)
			path.pop(aggs_name)

	async def process_buckets(self, path, parent, buckets):
		"""
		Recursive function for buckets processing.
		It iterates through keys of the dictionary, looking for 'buckets' or 'value'.
		If there are 'buckets', calls itself, if there is 'value', calls process_aggs
		and sends an event to process

		**Parameters**

		path :

		parent :

		buckets :

		"""
		for bucket in buckets:
			for k in bucket.keys():
				if k == 'key':
					path[parent] = bucket[k]
				elif isinstance(bucket[k], dict):
					await self.process_aggs(path, k, bucket[k])
