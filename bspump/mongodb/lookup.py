from ..abc.lookup import MappingLookup
from ..cache import CacheDict


class MongoDBLookup(MappingLookup):

	'''
The lookup that is linked with a MongoDB.
It provides a mapping (dictionary-like) interface to pipelines.
It feeds lookup data from MongoDB using a query.
It also has a simple cache to reduce a number of datbase hits.

Example:

class ProjectLookup(bspump.mongodb.MongoDBLookup):

	async def count(self, database):
		return await database['projects'].count_documents({})

	def find_one(self, database, key):
		return database['projects'].find_one({'_id':key})

	'''

	ConfigDefaults = {
		'database': '',  # Specify a database if you want to overload the connection setting
		'collection': '',  # Specify collection name
		'key': ''  # Specify key name used for search
	}

	def __init__(self, app, connection, id=None, config=None, cache=None):
		super().__init__(app, id=id, config=config)
		self.Connection = connection

		self.Database = self.Config['database']
		self.Collection = self.Config['collection']
		self.Key = self.Config['key']

		if len(self.Database) == 0:
			self.Database = self.Connection.Database

		self.Count = -1
		if cache is None:
			self.Cache = CacheDict()
		else:
			self.Cache = cache

		metrics_service = app.get_service('asab.MetricsService')
		self.CacheCounter = metrics_service.create_counter("mongodb.lookup", tags={}, init_values={'hit': 0, 'miss': 0})


	def _find_one(self, database, key):
		return database[self.Collection].find_one({self.Key: key})


	async def _count(self, database):
		return await database[self.Collection].count_documents({})


	async def load(self):
		self.Count = await self._count(self.Connection.Client[self.Database])


	def __len__(self):
		return self.Count


	def __getitem__(self, key):
		try:
			value = self.Cache[key]
			self.CacheCounter.add('hit', 1)
			return value
		except KeyError:
			database = self.Connection.Client[self.Database].delegate
			v = self._find_one(database, key)
			if v is not None:
				self.Cache[key] = v
			self.CacheCounter.add('miss', 1)
			return v


	def __iter__(self):
		database = self.Connection.Client[self.Database].delegate
		self.Iterator = database[self.Collection].find()
		return self

	def __next__(self):
		element = self.Iterator.next()
		key = element.get(self.Key)
		if key is not None:
			self.Cache[key] = element
		return key
