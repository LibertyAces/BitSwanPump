import abc
import requests
import json

from ..abc.lookup import MappingLookup

class ElasticSearchLookup(MappingLookup):

	'''
The lookup that is linked with a ES.
It provides a mapping (dictionary-like) interface to pipelines.
It feeds lookup data from ES using a query.
It also has a simple cache to reduce a number of datbase hits.

Example:

class ProjectLookup(bspump.elasticsearch.ElasticSearchLookup):

	async def count(self, database):
		return await database['projects'].count_documents({})

	def find_one(self, database, key):
		return database['projects'].find_one({'_id':key})

	'''

	ConfigDefaults = {
		'index': '', # Specify an index
		'key':'', # Specify field name to match
		'scroll_timeout': '1m',
	}

	def __init__(self, app, lookup_id, es_connection, config=None):
		super().__init__(app, lookup_id=lookup_id, config=config)
		self.Connection = es_connection

		self.Index = self.Config['index']
		self.ScrollTimeout = self.Config['scroll_timeout']
		self.Key = self.Config['key']

		self.Count = -1
		self.Cache = {}

		metrics_service = app.get_service('asab.MetricsService')
		self.CacheCounter = metrics_service.create_counter("es.lookup", tags={}, init_values={'hit': 0, 'miss': 0})


	
	def _find_one(self, key):
		prefix = '_search'
		request = {
			"size": 1,
			"query": {
				'match': {
					self.Key:key
				}
			}
		}
		url = self.Connection.get_url() + '{}/{}'.format(self.Index, prefix)
		response = requests.post(url, json=request)
		data = json.loads(response.text)
		try:
			hit = data['hits']['hits'][0]
		except IndexError:
			return None

		return hit["_source"]

	
	async def _count(self):
		prefix = "_count"
		request = {
			"query": {
				"match_all":{}
			}
		}

		url = self.Connection.get_url() + '{}/{}'.format(self.Index, prefix)
		
		async with self.Connection.get_session() as session:
			async with session.post(
				url,
				json=request,
				headers={'Content-Type': 'application/json'}
			) as response:

				if response.status != 200:
					data = await response.text() #!
					L.error("Failed to fetch data from ElasticSearch: {} from {}\n{}".format(response.status, url, data))
					

				msg = await response.json()

		return int(msg["count"])


	async def load(self):
		self.Count = await self._count()


	def __len__(self):
		return self.Count


	def __getitem__(self, key):
		try:
			value = self.Cache[key]
			self.CacheCounter.add('hit', 1)
			return value
		except KeyError:
			v = self._find_one(key)
			self.Cache[key] = v
			self.CacheCounter.add('miss', 1)
			return v


	def __iter__(self):
		scroll_id = None
		request = {
			"size":10000,
			"query": {
				"match_all":{}
			}
		}

		all_hits = []
		while True:
			if scroll_id is None:
				path = '{}/_search?scroll={}'.format(self.Index, self.ScrollTimeout)
				request_body = request
			else:
				path = "_search/scroll"
				request_body = {"scroll": self.ScrollTimeout, "scroll_id": scroll_id}

			url = self.Connection.get_url() + path
			response = requests.post(url, json=request_body)
			
			if response.status_code != 200:
				data = response.text()
				L.error("Failed to fetch data from ElasticSearch: {} from {}\n{}".format(response.status, url, data))
				break
			
			data = json.loads(response.text)

			scroll_id = data.get('_scroll_id')
			
			if scroll_id is None:
				break

			hits = data['hits']['hits']
			
			if len(hits) == 0:
				break
			
			all_hits.extend(hits)
		
		self.Iterator = all_hits.__iter__()
		return self


	def __next__(self):
		element = next(self.Iterator)

		key = element['_source'].get(self.Key)
		if key is not None:
			self.Cache[key] = element['_source']
		return key
