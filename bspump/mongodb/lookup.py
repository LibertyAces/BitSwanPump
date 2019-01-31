import abc

from ..abc.lookup import MappingLookup

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
		'database': '', # Specify a database if you want to overload the connection setting
		'collection':'', # Specify collection name
		'key':'' # Specify key name used for search
	}

	def __init__(self, app, lookup_id, mongodb_connection, config=None):
		super().__init__(app, lookup_id=lookup_id, config=config)
		self.Connection = mongodb_connection

		self.Database = self.Config['database']
		if len(self.Database) == 0:
			self.Database = self.Connection.Database

		self.Count = -1
		self.Cache = {}

		metrics_service = app.get_service('asab.MetricsService')
		self.CacheCounter = metrics_service.create_counter("mongodb.lookup", tags={}, init_values={'hit': 0, 'miss': 0})


	def _find_one(self, database, key):
		
		return database[self.Config['collection']].find_one({self.Config['key']:key})

	
	async def _count(self, database):

		return await database[self.Config['collection']].count_documents({})


	async def load(self):
		self.Count = await self._count(self.Connection.Client[self.Database])


	def __len__(self):
		return self.Count


	def __getitem__(self, key):
		try:
			key = self.Cache[key]
			self.CacheCounter.add('hit', 1)
			return key
		except KeyError:
			# Find pymongo (synchronous) connection to a database
			database = self.Connection.Client[self.Database].delegate
			v = self._find_one(database, key)
			self.Cache[key] = v
			self.CacheCounter.add('miss', 1)
			return v

	def __iter__(self):
		database = self.Connection.Client[self.Database].delegate
		collection = self.Config['collection']
		return database[collection].find().__iter__()
