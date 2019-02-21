import abc

from ..abc.lookup import MappingLookup
import aiomysql.cursors
import pymysql.cursors
import pymysql




class MySQLLookup(MappingLookup):

	'''
The lookup that is linked with a MySQL.
It provides a mapping (dictionary-like) interface to pipelines.
It feeds lookup data from MongoDB using a query.
It also has a simple cache to reduce a number of datbase hits.

Example:

class ProjectLookup(bspump.mysql.MySQLLookup):

	async def count(self, database):
		return await database['projects'].count_documents({})

	def find_one(self, database, key):
		return database['projects'].find_one({'_id':key})

	'''

	ConfigDefaults = {
		'table': '', # Specify a database if you want to overload the connection setting
		'key':'' # Specify key name used for search
	}

	def __init__(self, app, lookup_id, mysql_connection, config=None):
		super().__init__(app, lookup_id=lookup_id, config=config)
		self.Connection = mysql_connection

		self.Table = self.Config['table']
		self.Key = self.Config['key']

		self.Count = -1
		self.Cache = {}

		conn_sync = pymysql.connect(host=mysql_connection._host,
					 user=mysql_connection._user,
					 passwd=mysql_connection._password,
					 db=mysql_connection._db)
		self.CursorSync = pymysql.cursors.DictCursor(conn_sync)
		self.CursorAsync = None

		metrics_service = app.get_service('asab.MetricsService')
		self.CacheCounter = metrics_service.create_counter("mysql.lookup", tags={}, init_values={'hit': 0, 'miss': 0})


	def _find_one(self, key):
		query = "SELECT * FROM {} WHERE {}='{}'".format(self.Table, self.Key, key)
		self.CursorSync.execute(query)
		result = self.CursorSync.fetchone()
		return result

	
	async def _count(self):

		query = """SELECT COUNT(*) as "Number_of_Rows" FROM {};""".format(self.Table)
		await self.CursorAsync.execute(query)
		count = await self.CursorAsync.fetchone()
		return count['Number_of_Rows']


	async def load(self):
		await self.Connection.ConnectionEvent.wait()
		conn_async = await self.Connection.acquire()
		self.CursorAsync = await conn_async.cursor(aiomysql.cursors.DictCursor)
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
		query = query = "SELECT * FROM {}".format(self.Table)
		self.CursorSync.execute(query)
		result = self.CursorSync.fetchall()
		self.Iterator = result.__iter__()
		return self


	def __next__(self):
		element = next(self.Iterator)
		key = element.get(self.Key)
		if key is not None:
			self.Cache[key] = element
		return key
