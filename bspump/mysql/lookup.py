import logging
import aiomysql

from ..abc.lookup import MappingLookup
from ..abc.lookup import AsyncLookupMixin
from ..cache import CacheDict

##

L = logging.getLogger(__name__)

##


class MySQLLookup(MappingLookup, AsyncLookupMixin):

	'''
MySQLLookup is linked with a MySQL.
MySQLLookup provides a mapping (dictionary-like) interface to pipelines.
MySQLLookup expects user to obtain values asynchronously in an enricher based on Generator.
MySQLLookup feeds lookup data from MySQL database using a query.
MySQLLookup also has a simple cache to reduce a number of database hits.

MySQLLookup allows to specify custom cache strategy via `cache` parameter, as shown in the example below.
LRUCacheDict removes last used elements, if the time they were lastly used exceeds the specified `max_duration` or the cache dictionary exceeds `max_size`.
For more information, please see: https://en.wikipedia.org/wiki/Cache_replacement_policies#Least_recently_used_(LRU)

First, it is needed to create MySQLLookup instance and register it inside the BSPump service:

	self.MySQLLookup =  MySQLLookup(self,
		connection=mysql_connection,
		id="MySQLLookup",
		cache=bspump.cache.LRUCacheDict(app, max_size=1000, max_duration=1000)
		config={
			'from': 'user_loc',
			'key': 'user'
		})
	svc = app.get_service("bspump.PumpService")
	svc.add_lookup(self.MySQLLookup)

The configuration option "from" can include a table name ...

	from="Orders"

...or a query string including joins like:

	from="Orders INNER JOIN Customers ON Orders.CustomerID=Customers.CustomerID"

The MySQLLookup can be then located and used inside a custom enricher:

	class AsyncEnricher(bspump.Generator):

		def __init__(self, app, pipeline, id=None, config=None):
			super().__init__(app, pipeline, id, config)
			svc = app.get_service("bspump.PumpService")
			self.Lookup = svc.locate_lookup("MySQLLookup")

		async def generate(self, context, event, depth):
			if 'user' not in event:
				return None

			info = await self.Lookup.get(event['user'])

			# Inject a new event into a next depth of the pipeline
			await self.Pipeline.inject(context, event, depth)

	'''

	ConfigDefaults = {
		'statement': '*',  # Specify the statement what to select
		'from': '',  # Specify the FROM object, which can be a table or a query string
		'key': '',  # Specify key name used for search
		'query_find_one': 'SELECT {} FROM {} WHERE {}=%s;',  # Specify query string to find one record in database using key
		'query_count': 'SELECT COUNT(*) as \'count\' FROM {};',  # Specify query string to count number of records in the database
		'query_iter': 'SELECT {} FROM {};',  # Specify general query string for the iterator
	}

	def __init__(self, app, connection, id=None, config=None, cache=None):
		super().__init__(app, id=id, config=config)
		self.Connection = connection

		self.Statement = self.Config['statement']
		self.From = self.Config['from']
		self.Key = self.Config['key']

		self.QueryFindOne = self.Config['query_find_one']
		self.QueryCount = self.Config['query_count']
		self.QueryIter = self.Config['query_iter']

		self.Count = -1
		if cache is None:
			self.Cache = CacheDict()
		else:
			self.Cache = cache

		metrics_service = app.get_service('asab.MetricsService')
		self.CacheCounter = metrics_service.create_counter("mysql.lookup.cache", tags={}, init_values={'hit': 0, 'miss': 0})
		self.SuccessCounter = metrics_service.create_counter("mysql.lookup.success", tags={}, init_values={'hit': 0, 'miss': 0})

	async def _find_one(self, key):
		query = self.QueryFindOne.format(self.Statement, self.From, self.Key)
		async with self.Connection.acquire_connection() as connection:
			async with connection.cursor(aiomysql.cursors.DictCursor) as cursor_async:
				await cursor_async.execute(query, key)
				result = await cursor_async.fetchone()
				return result


	async def _count(self):
		query = self.QueryCount.format(self.From)
		async with self.Connection.acquire_connection() as connection:
			async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
				await cursor.execute(query)
				result = await cursor.fetchone()
				return result['count']

	async def get(self, key):
		"""
		Obtain the value from lookup asynchronously.
		"""

		try:
			value = self.Cache[key]
			self.CacheCounter.add('hit', 1)
		except KeyError:
			value = await self._find_one(key)
			self.Cache[key] = value
			self.CacheCounter.add('miss', 1)

		if value is None:
			self.SuccessCounter.add('miss', 1)
		else:
			self.SuccessCounter.add('hit', 1)

		return value

	async def load(self):
		await self.Connection.ConnectionEvent.wait()
		self.Count = await self._count()

	def __len__(self):
		return self.Count

	def __getitem__(self, key):
		# To avoid synchronous operations completely
		raise NotImplementedError()

	def __iter__(self):
		query = self.QueryIter.format(self.Statement, self.From)
		cursor_sync = self.Connection.acquire_sync_cursor()
		cursor_sync.execute(query)
		result = cursor_sync.fetchall()
		self.Iterator = result.__iter__()
		return self

	def __next__(self):
		element = next(self.Iterator)
		key = element.get(self.Key)
		if key is not None:
			self.Cache[key] = element
		return key
