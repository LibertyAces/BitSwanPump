import logging

from ..abc.source import TriggerSource

L = logging.getLogger(__name__)


class ElasticSearchSource(TriggerSource):
	"""
	Description:

	:return:
	"""
	ConfigDefaults = {
		'index': 'index-*',
		'scroll_timeout': '1m',

	}

	def __init__(self, app, pipeline, connection, request_body=None, paging=True, id=None, config=None):
		"""
		Description:

		:return:
		"""
		super().__init__(app, pipeline, id=id, config=config)
		self.Connection = pipeline.locate_connection(app, connection)

		self.Index = self.Config['index']
		self.ScrollTimeout = self.Config['scroll_timeout']
		self.Paging = paging

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
				}}

	async def cycle(self):
		"""
		Description:

		:return:
		"""
		scroll_id = None

		while True:
			if scroll_id is None:
				path = '{}/_search?scroll={}'.format(self.Index, self.ScrollTimeout)
				request_body = self.RequestBody
			else:
				path = "_search/scroll"
				request_body = {"scroll": self.ScrollTimeout, "scroll_id": scroll_id}

			url = self.Connection.get_url() + path
			async with self.Connection.get_session() as session:
				async with session.post(
					url,
					json=request_body,
					headers={'Content-Type': 'application/json'}
				) as response:

					if response.status != 200:
						data = await response.text()
						L.error("Failed to fetch data from ElasticSearch: {} from {}\n{}".format(response.status, url, data))
						break

					msg = await response.json()

			scroll_id = msg.get('_scroll_id')
			if scroll_id is None:
				break

			hits = msg['hits']['hits']
			if len(hits) == 0:
				break

			# Feed messages into a pipeline
			for hit in hits:
				await self.process(hit['_source'])

			if not self.Paging:
				break


class ElasticSearchAggsSource(TriggerSource):
	"""
	Description: d

	:return:
	"""
	ConfigDefaults = {
		'index': 'index-*',
	}

	def __init__(self, app, pipeline, connection, request_body=None, id=None, config=None):
		"""
		Description:

		:return:
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
		Description:

		:return:
		"""
		request_body = self.RequestBody
		path = '{}/_search?'.format(self.Index)
		url = self.Connection.get_url() + path
		async with self.Connection.get_session() as session:
			async with session.post(
				url,
				json=request_body,
				headers={'Content-Type': 'application/json'}
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

		:return:
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
		Description: Recursive function for buckets processing.
		It iterates through keys of the dictionary, looking for 'buckets' or 'value'.
		If there are 'buckets', calls itself, if there is 'value', calls process_aggs
		and sends an event to process

		:return:
		"""
		for bucket in buckets:
			for k in bucket.keys():
				if k == 'key':
					path[parent] = bucket[k]
				elif isinstance(bucket[k], dict):
					await self.process_aggs(path, k, bucket[k])
