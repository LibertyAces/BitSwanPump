import asyncio
import logging
import socket
import aiomysql
import pymysql.err
import pymysql.cursors
from aiomysql import create_pool
from asab import PubSub

from ..abc.connection import Connection

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
		'connect_timeout': 1,
		'reconnect_delay': 5.0,
		'output_queue_max_size': 10,
		'max_bulk_size': 2,
	}

	def __init__(self, app, id=None, config=None):
		super().__init__(app, id=id, config=config)

		self.ConnectionEvent = asyncio.Event(loop=app.Loop)
		self.ConnectionEvent.clear()

		self.PubSub = PubSub(app)
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



		self._conn_future = None
		self._connection_request = False
		self._pause = False

		# Subscription
		self._on_health_check('connection.open!')
		app.PubSub.subscribe("Application.stop!", self._on_application_stop)
		app.PubSub.subscribe("Application.tick!", self._on_health_check)
		app.PubSub.subscribe("MySQLConnection.pause!", self._on_pause)
		app.PubSub.subscribe("MySQLConnection.unpause!", self._on_unpause)

		self._output_queue = asyncio.Queue(loop=app.Loop)
		self._bulks = {} # We have a "bulk" per query


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
			except:
				# Connection future threw an error
				L.exception("Unexpected connection future error")
				
			# Connection future already resulted (with or without exception)
			self._conn_future = None

		assert(self._conn_future is None)

		self._conn_future = asyncio.ensure_future(
			self._connection(),
			loop=self.Loop
		)


	async def _connection(self):
		try:
			async with create_pool(
				host=self._host,
				port=self._port,
				user=self._user,
				password=self._password,
				db=self._db,
				connect_timeout=self._connect_timeout, #Doesn't work! See socket.timeout exception below
				loop=self.Loop) as pool:

				self._conn_pool = pool
				self.ConnectionEvent.set()
				await self._loader()
		except socket.timeout:
			# Socket timeout not implemented in aiomysql as it sets a keepalive to the connection
			# it has been placed as an issue on GitHub: https://github.com/aio-libs/aiomysql/issues/257
			L.exception("MySQL connection timeout")
			pass
		except BaseException:
			L.exception("Unexpected MySQL connection error")
			raise


	def acquire(self):
		assert(self._conn_pool is not None)
		return self._conn_pool.acquire()


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

			try:
				async with self.acquire() as conn:
					try:
						async with conn.cursor() as cur:
							await cur.executemany(query, data)
							await conn.commit()
					except BaseException as e:
						L.exception("Unexpected error when processing MySQL query.")
			except BaseBaseException as e:
				L.exception("Couldn't acquire connection")

