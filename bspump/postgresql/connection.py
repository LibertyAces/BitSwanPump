import asyncio
import logging

import aiopg
import aiopg.utils

import psycopg2
import psycopg2.errorcodes
import psycopg2.extras

import asab
from ..abc.connection import Connection


L = logging.getLogger(__name__)


class PostgreSQLConnection(Connection):


	ConfigDefaults = {
		'host': '127.0.0.1',
		'port': 5432,
		'user': '',
		'password': '',
		'db': '',
		'connect_timeout': 60,
		'reconnect_delay': 5.0,
		'output_queue_max_size': 10,
		'max_bulk_size': 1,  # This is because execute many is not supported by aiopg
	}

	# This is just guess work based on the existing MySQL retryables
	# This doesn't work for connection errors for sync_connection
	RetryErrors = frozenset([
		psycopg2.errorcodes.ADMIN_SHUTDOWN,
		psycopg2.errorcodes.CRASH_SHUTDOWN,
		psycopg2.errorcodes.CANNOT_CONNECT_NOW,
		psycopg2.errorcodes.CONNECTION_FAILURE,
		psycopg2.errorcodes.CONNECTION_EXCEPTION,
		psycopg2.errorcodes.SQLSERVER_REJECTED_ESTABLISHMENT_OF_SQLCONNECTION,
		psycopg2.errorcodes.SQLCLIENT_UNABLE_TO_ESTABLISH_SQLCONNECTION,
		psycopg2.errorcodes.CLASS_INVALID_TRANSACTION_INITIATION,
		psycopg2.errorcodes.TOO_MANY_CONNECTIONS,
		psycopg2.errorcodes.QUERY_CANCELED])

	def __init__(self, app, id=None, config=None):
		super().__init__(app, id=id, config=config)

		self.ConnectionEvent = asyncio.Event()
		self.ConnectionEvent.clear()

		self.PubSub = asab.PubSub(app)
		self.Loop = app.Loop

		self._host = self.Config['host']
		self._port = int(self.Config['port'])
		self._user = self.Config['user']
		self._password = self.Config['password']
		self._connect_timeout = self.Config['connect_timeout']
		self._db = self.Config['db']
		self._reconnect_delay = self.Config['reconnect_delay']
		self._output_queue_max_size = self.Config['output_queue_max_size']
		self._max_bulk_size = int(self.Config['max_bulk_size'])

		self._conn_sync = None
		self._conn_future = None
		self._connection_request = False
		self._pause = False

		# Subscription
		self._on_health_check('connection.open!')
		app.PubSub.subscribe("Application.stop!", self._on_application_stop)
		app.PubSub.subscribe("Application.tick!", self._on_health_check)
		app.PubSub.subscribe("PostgreSQLConnection.pause!", self._on_pause)
		app.PubSub.subscribe("PostgreSQLConnection.unpause!", self._on_unpause)

		self._output_queue = asyncio.Queue(loop=app.Loop)
		self._bulks = {}  # We have a "bulk" per query


	def _on_pause(self):
		self._pause = True

	def _on_unpause(self):
		self._pause = False


	def _flush(self):
		for query in self._bulks.keys():
			# Break if throttling was requested during the flush,
			# so that put_nowait doesn't raise
			if self._pause:
				break

			self._flush_bulk(query)

	def _flush_bulk(self, query):

		# Enqueue and thorttle if needed
		self._output_queue.put_nowait((query, self._bulks[query]))
		if self._output_queue.qsize() == self._output_queue_max_size:
			self.PubSub.publish("PostgreSQLConnection.pause!", self)

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

		# Connection future already resulted (with or without exception)
		self._sync_connection()

	def build_dsn(self):
		dsn = ""
		# Database
		# if len(self._db) > 0:
		dsn += "dbname={} ".format(self._db)

		# Host
		# if len(self._host) > 0:
		dsn += "host={} ".format(self._host)

		# Port
		# if self._port is not None:
		dsn += "port={} ".format(self._port)

		# User
		if len(self._user) > 0:
			dsn += "user={} ".format(self._user)

		# Password
		if len(self._password):
			dsn += "password={} ".format(self._password)

		dsn = dsn.strip()
		return dsn

	async def _async_connection(self):
		dsn = self.build_dsn()

		try:
			async with aiopg.create_pool(
				dsn=dsn,
				timeout=self._connect_timeout,
				loop=self.Loop) as pool:

				self._conn_pool = pool
				self.ConnectionEvent.set()

				await self._loader()

		except (psycopg2.OperationalError, psycopg2.ProgrammingError, psycopg2.InternalError) as e:
			if e.pgcode in self.RetryErrors:
				L.warning("Recoverable error '{}' ({}) occurred in PostgreSQLConnection.".format(e.pgerror, e.pgcode))
				return None
			raise e
		except BaseException as e:
			L.exception("Unexpected PostgresSQL connection error. %s" % e)
			raise


	def acquire(self) -> aiopg.pool._PoolConnectionContextManager:
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

	def _sync_connection(self):
		"""
		Acquire synchronous psycopg2 connection
		Currently only used for iterating over a PostgreSQLLookup
		"""
		dsn = self.build_dsn()
		if self._conn_sync is not None:
			try:
				self._conn_sync.close()
			except (psycopg2.OperationalError, psycopg2.ProgrammingError, psycopg2.InternalError):
				pass
			self._conn_sync = None
		try:
			connection = psycopg2.connect(
				dsn=dsn,
				connect_timeout=self._connect_timeout)
			self._conn_sync = connection
		except (psycopg2.OperationalError, psycopg2.ProgrammingError, psycopg2.InternalError) as e:
			if e.pgcode in self.RetryErrors:
				L.warning("Recoverable error '{}' ({}) occurred in PostgreSQLConnection.".format(e.pgerror, e.pgcode))
				return None
			L.exception("Unexpected PostgreSQL (psycopg2) connection error")
			raise e
		except BaseException:
			L.exception("Unexpected PostgreSQL (psycopg2) connection error")

			raise

	def acquire_sync_cursor(self) -> psycopg2.extras.DictCursor:
		"""
		Acquire synchronous psycopg2 cursor
		Currently only used for iterating over a PostgreSQLLookup
		"""
		assert(self._conn_sync is not None)
		return self._conn_sync.cursor(cursor_factory=psycopg2.extras.DictCursor)


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
					self.PubSub.publish("PostgreSQLConnection.unpause!", self, asynchronously=True)

			try:
				async with self.acquire() as conn:
					try:
						async with conn.cursor() as cur:
							for item in data:
								_query = cur.mogrify(query, item)
								await cur.execute(_query)
					except BaseException:
						L.exception("Unexpected error when processing PostgreSQL query.")
			except BaseException:
				L.exception("Couldn't acquire connection")
