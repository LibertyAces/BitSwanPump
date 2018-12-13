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
	}

	def __init__(self, app, lookup_id, mongodb_connection, config=None):
		super().__init__(app, lookup_id=lookup_id, config=config)
		self.Connection = mongodb_connection

		self.Database = self.Config['database']
		if len(self.Database) == 0:
			self.Database = self.Connection.Database

		self.Count = -1
		self.Cache = {}


	@abc.abstractmethod
	def find_one(self, database, key):
		'''
		return database['collection'].find_one({'key':key})
		'''
		pass


	@abc.abstractmethod
	async def count(self, database):
		'''
		return await database['collection'].count_documents({})
		'''
		pass


	async def load(self):
		self.Count = await self.count(self.Connection.Client[self.Database])


	def __len__(self):
		return self.Count


	def __getitem__(self, key):
		try:
			return self.Cache[key]
		except KeyError:
			# Find pymongo (synchronous) connection to a database
			database = self.Connection.Client[self.Database].delegate
			v = self.find_one(database, key)
			self.Cache[key] = v
			return v

	def __iter__(self):
		raise NotImplementedError("Not implemented yet") #TODO: This ...