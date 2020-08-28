from ..abc.lookup import MappingLookup
from ..abc.lookup import AsyncLookupMixin
from ..cache import CacheDict
import asyncio
import logging

###

L = logging.getLogger(__name__)

###


class MongoDBLookup(MappingLookup, AsyncLookupMixin):
	"""
	The lookup that is linked with a MongoDB.
	It provides a mapping (dictionary-like) interface to pipelines.
	It feeds lookup data from Mongo using a query.
	It also has a simple cache to reduce a number of database hits.

	**configs**

	*database* - Mongo database name

	*collection* - Mongo collection name

	*key* - field name to match


	Example:

.. code:: python

The MongoDBLookup can be then located and used inside a custom enricher:

	class AsyncEnricher(bspump.Generator):

		def __init__(self, app, pipeline, id=None, config=None):
			super().__init__(app, pipeline, id, config)
			svc = app.get_service("bspump.PumpService")
			self.Lookup = svc.locate_lookup("MyMongoLookup")

		async def generate(self, context, event, depth):
			if 'user' not in event:
				return None

			info = await self.Lookup.get(event['user'])

			# Inject a new event into a next depth of the pipeline
			self.Pipeline.inject(context, event, depth)

	"""

	ConfigDefaults = {
		'database': '',  # Specify a database if you want to overload the connection setting
		'collection': '',  # Specify collection name
		'key': '',  # Specify key name used for search
		'changestream': False
	}

	@classmethod
	def construct(cls, app, definition: dict, connection_id="MongoDBConnection"):
		"""
		Usage:

			---
			lookup: UserPasswordLookup
			config:
				database: lookups
				collection: userpassword
				key: user
		"""

		# TODO: Think about declarativity in lookups
		_id = definition.get("id", definition.get("declaration"))
		config = definition.get("config")
		svc = app.get_service("bspump.PumpService")
		mongodb_connection = svc.locate_connection(connection_id)
		return cls(app, connection=mongodb_connection, id=_id, config=config)

	def __init__(self, app, connection, id=None, config=None, cache=None):
		super().__init__(app, id=id, config=config)
		self.Connection = connection
		self.Database = self.Config['database']
		self.Collection = self.Config['collection']
		self.Key = self.Config['key']
		self.Changestream = self.Config.getboolean("changestream")

		self.Loop = app.Loop
		self._changestream_future = None

		if len(self.Database) == 0:
			self.Database = self.Connection.Database

		if self.Changestream:
			self._changestream_future = asyncio.ensure_future(
				self._changestream(),
				loop=self.Loop,
			)

		self.Count = -1
		if cache is None:
			self.Cache = CacheDict()
		else:
			self.Cache = cache

		metrics_service = app.get_service('asab.MetricsService')
		self.CacheCounter = metrics_service.create_counter("mongodb.lookup", tags={}, init_values={'hit': 0, 'miss': 0})
		self.SuccessCounter = \
			metrics_service.create_counter("mongodb.lookup.success", tags={}, init_values={'hit': 0, 'miss': 0})

		app.PubSub.subscribe('Application.tick/10!', self._on_health_check)
		app.PubSub.subscribe("Application.exit!", self._on_exit)


	def _on_health_check(self, message_type):
		if self._changestream_future is not None and self.Changestream:
			# Future exists

			if not self._changestream_future.done():
				# Future didn't result yet
				# No sanitization needed
				return

			try:
				self._changestream_future.result()
			except Exception:
				# Connection future threw an error
				L.exception("Unexpected connection future error")

			# Future already resulted (with or without exception)
			self._changestream_future = None

		assert(self._changestream_future is None)

		if self.Changestream:
			self._changestream_future = asyncio.ensure_future(
				self._changestream(),
				loop=self.Loop,
			)

	async def _on_exit(self, message_type):
		# On application exit, we cancel the future.
		if self._changestream_future is not None:
			self._changestream_future.cancel()

	def build_query(self, key):
		return {self.Key: key}

	async def _find_one(self, query):
		return await (self.Connection.Client[self.Database][self.Collection]).find_one(query)

	async def _changestream(self):
		try:
			async with self.Connection.Client[self.Database][self.Collection].watch() as stream:
				async for change in stream:
					self.Cache.clear()

		except asyncio.CancelledError:
			return

		except Exception as e:
			L.exception(f"Observed exception: {e}")
			await asyncio.sleep(5)

	async def get(self, key):
		"""
		Obtain the value from lookup asynchronously.
		"""
		try:
			value = self.Cache[key]
			self.CacheCounter.add('hit', 1)
		except KeyError:
			query = self.build_query(key)
			value = await self._find_one(query)
			if value is not None:
				self.Cache[key] = value
				self.CacheCounter.add('miss', 1)

		if value is None:
			self.SuccessCounter.add('miss', 1)
		else:
			self.SuccessCounter.add('hit', 1)
		return value

	async def _count(self, database):
		return await database[self.Collection].count_documents({})

	async def load(self):
		return True

	def __len__(self):
		return self.Count

	def __getitem__(self, key):
		raise NotImplementedError()

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
