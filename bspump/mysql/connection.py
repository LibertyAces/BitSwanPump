import asyncio
import logging

import aiomysql
import aiomysql.utils

import pymysql
import pymysql.cursors
import pymysql.err

from ..abc.connection import Connection
from .convertors import convertors

#

L = logging.getLogger(__name__)

#


class MySQLConnection(Connection):

	"""
	MySQLConnection is a top BitSwan object, that is used to connect the application to an external MySQL database.
	MySQLConnection is thus used in MySQL-related sources, sinks, processors and lookups such as MySQLLookup.

	MySQLConnection is built on top of aiomysql library and utilizes its functions: https://aiomysql.readthedocs.io/en/latest/

	The following code illustrates how to create and register the MySQL connection inside the application object.
	The connection's ID is set to "MySQLConnection" (the second argument of the connection's constructor),
	which is also then used as a section name in configuration files.

.. code:: python

	app = bspump.BSPumpApplication()
	svc = app.get_service("bspump.PumpService")
	svc.add_connection(
		bspump.mysql.MySQLConnection(app, "MySQLConnection")
	)

	In order to locate MySQLConnection in the constructor method of sources, sinks, processors etc., the following code can be used:

.. code:: python

	svc = app.get_service("bspump.PumpService")
	connection = svc.locate_connection("MySQLConnection")

	"""

	ConfigDefaults = {
		'host': 'localhost',
		'port': 3306,
		'user': '',
		'password': '',
		'db': '',
		'connect_timeout': 10,
		'reconnect_delay': 5.0,
		'output_queue_max_size': 100,
		'max_bulk_size': 5,
		'autocommit': True,
		'connection_pool_minsize': 1,
		'connection_pool_maxsize': 10,
	}

	RetryErrors = frozenset([1047, 1053, 1077, 1078, 1079, 1080, 2003, 2006, 2012, 2013, 1152, 1205, 1213, 1223])

	def __init__(self, app, id=None, config=None):
		super().__init__(app, id=id, config=config)

		self.ConnectionEvent = asyncio.Event(loop=app.Loop)
		self.ConnectionEvent.clear()

		self.PubSub = app.PubSub
		self.Loop = app.Loop

		self._host = self.Config['host']
		self._port = int(self.Config['port'])
		self._user = self.Config['user']
		self._password = self.Config['password']
		self._connect_timeout = int(self.Config['connect_timeout'])
		self._db = self.Config['db']
		self._reconnect_delay = float(self.Config['reconnect_delay'])
		self._output_queue_max_size = int(self.Config['output_queue_max_size'])
		self._max_bulk_size = int(self.Config['max_bulk_size'])
		self._autocommit = self.Config.getboolean('autocommit')

		self._conn_future = None
		self._conn_pool = None
		self._conn_sync = None
		self._connection_request = False
		self._pause = False
		self._throttled_by_error = False

		# Size of connection pool
		self.ConnectionPoolMinSize = self.Config["connection_pool_minsize"]
		self.ConnectionPoolMaxSize = self.Config["connection_pool_maxsize"]

		# Subscription
		self._on_health_check('connection.open!')
		app.PubSub.subscribe("Application.stop!", self._on_application_stop)
		app.PubSub.subscribe("Application.tick!", self._on_health_check)
		app.PubSub.subscribe("MySQLConnection.pause!", self._on_pause)
		app.PubSub.subscribe("MySQLConnection.unpause!", self._on_unpause)

		self._output_queue = asyncio.Queue(loop=app.Loop)
		self._bulks = {}  # We have a "bulk" per query


	def _on_pause(self, event_type, connection):
		self._pause = True

	def _on_unpause(self, event_type, connection):
		self._pause = False


	def _flush(self):
		for query in self._bulks.keys():
			# Break if throttling was requested during the flush,
			# so that put_nowait doesn't raise
			if self._pause:
				break

			self._flush_bulk(query)

	def _flush_bulk(self, query):

		# Enqueue and throttle if needed
		self._output_queue.put_nowait((query, self._bulks[query]))
		if self._output_queue.qsize() == self._output_queue_max_size:
			self.PubSub.publish("MySQLConnection.pause!", self)

		# Reset bulk
		self._bulks[query] = []


	def _on_application_stop(self, message_type, counter):
		self._flush()
		self._output_queue.put_nowait((None, None))


	def _on_health_check(self, message_type):
		if self._conn_future is not None:
			# Connection future exists

			if not self._conn_future.done():
				# Connection future didn't result yet
				# No sanitization needed
				return

			try:
				self._conn_future.result()
			except Exception:
				# Connection future threw an error
				L.exception("Unexpected connection future error")

			# Connection future already resulted (with or without exception)
			self._conn_future = None

		assert(self._conn_future is None)

		self._conn_future = asyncio.ensure_future(
			self._async_connection(),
			loop=self.Loop
		)

		self._sync_connection()


	async def _async_connection(self):
		# Erase the previous connections
		if self._conn_pool is not None:
			try:
				self._conn_pool.close()
				await self._conn_pool.wait_closed()
			except (pymysql.err.InternalError, pymysql.err.ProgrammingError, pymysql.err.OperationalError):
				pass
			self._conn_pool = None

		try:
			async with aiomysql.create_pool(
				host=self._host,
				port=self._port,
				user=self._user,
				password=self._password,
				db=self._db,
				conv=convertors,
				connect_timeout=self._connect_timeout,
				autocommit=self._autocommit,
				minsize=self.ConnectionPoolMinSize,
				maxsize=self.ConnectionPoolMaxSize,
				loop=self.Loop) as pool:

				self._conn_pool = pool
				self.ConnectionEvent.set()

				# Ensures that all connections are utilized
				loaders = []
				for index in range(0, self.ConnectionPoolMaxSize):
					loaders.append(asyncio.ensure_future(self._loader()))
				await asyncio.wait(loaders, return_when=asyncio.ALL_COMPLETED)

		except (pymysql.err.InternalError, pymysql.err.ProgrammingError, pymysql.err.OperationalError) as e:
			if e.args[0] in self.RetryErrors:
				L.warn("Recoverable error '{}' occurred in MySQLConnection. Retrying.".format(e.args[0]))
				self._conn_future = None
				return
			L.exception("Unexpected MySQL connection error")
			raise e
		except BaseException:
			L.exception("Unexpected MySQL connection error")
			raise


	def _sync_connection(self):
		# Close the connection first
		if self._conn_sync is not None:
			try:
				self._conn_sync.close()
			except (pymysql.err.InternalError, pymysql.err.ProgrammingError, pymysql.err.OperationalError):
				pass
			self._conn_sync = None

		try:
			connection = pymysql.connect(
				host=self._host,
				port=self._port,
				user=self._user,
				password=self._password,
				database=self._db,
				conv=convertors,
				autocommit=self._autocommit,
				connect_timeout=self._connect_timeout)
			self._conn_sync = connection
		except (pymysql.err.InternalError, pymysql.err.ProgrammingError, pymysql.err.OperationalError) as e:
			if e.args[0] in self.RetryErrors:
				L.warn("Recoverable error '{}' occurred in MySQLConnection. Retrying.".format(e.args[0]))
				return
			L.exception("Unexpected MySQL connection error")
			raise e
		except BaseException:
			L.exception("Unexpected MySQL connection error")
			raise


	def acquire_connection(self) -> aiomysql.utils._PoolAcquireContextManager:
		"""
		Acquire asynchronous database connection

		Use with `async with` statement

	.. code-block:: python

		async with self.Connection.acquire_connection() as connection:
			async with connection.cursor() as cursor:
				await cursor.execute(query)

		:return: Asynchronous Context Manager
		"""
		assert(self._conn_pool is not None)
		return self._conn_pool.acquire()


	def acquire_sync_cursor(self) -> pymysql.cursors.DictCursor:
		"""
		Acquire synchronous database cursor

		Use with `with` statement

	.. code-block:: python

		with self.Connection.acquire_sync_cursor() as cursor:
			await cursor.execute(query)

		:return: Context Manager
		"""
		assert(self._conn_sync is not None)
		return pymysql.cursors.DictCursor(self._conn_sync)


	def consume(self, query, data):
		# Create a bulk for this query if doesn't yet exist
		if query not in self._bulks:
			self._bulks[query] = []

		# Add data to the query's bulk
		self._bulks[query].append(data)

		# Flush on _max_bulk_size
		if len(self._bulks[query]) >= self._max_bulk_size:
			self._flush_bulk(query)


	async def _loader(self):
		while True:
			query, data = await self._output_queue.get()

			if query is None:
				break

			if self._output_queue.qsize() == self._output_queue_max_size - 1:
					self.PubSub.publish("MySQLConnection.unpause!", self, asynchronously=True)

			async with self.acquire_connection() as connection:
				async with connection.cursor() as cursor:
					try:
						await cursor.executemany(query, data)
						await connection.commit()
						if self._throttled_by_error:
							self.Pipeline.throttle(self, False)
							self._throttled_by_error = False
					except (pymysql.err.InternalError, pymysql.err.ProgrammingError, pymysql.err.OperationalError) as e:
						if e.args[0] in self.RetryErrors:
							L.warn("Recoverable error '{}' occurred in MySQLConnection. Retrying.".format(e.args[0]))
							self._output_queue.put_nowait((query, data))
							self.Pipeline.throttle(self, True)
							self._throttled_by_error = True
						raise e
