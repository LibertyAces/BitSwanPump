import asyncio
import logging
import aiomysql
import pymysql.err
from aiomysql import create_pool
from asab import PubSub

from ..abc.connection import Connection

#

L = logging.getLogger(__name__)

#

class MySQLConnection(Connection):


	ConfigDefaults = {
		'host': 'localhost',
		'port': 3306,
		'user': 'root',
		'password': 'root',
		'db': 'test',
		'reconnect_delay': 1.0,
	}

	def __init__(self, app, connection_id, config=None):
		super().__init__(app, connection_id, config=config)

		self.Connection = None
		self.ConnectionEvent = asyncio.Event(loop=app.Loop)
		self.ConnectionEvent.clear()

		self.PubSub = PubSub(app)
		self.Loop = app.Loop

		self._host = self.Config['host']
		self._port = self.Config['port']
		self._user = self.Config['user']
		self._password = self.Config['password']
		self._db = self.Config['db']
		self._reconnect_delay = self.Config['reconnect_delay']

		asyncio.ensure_future(self._reconnect(), loop = self.Loop)


	async def _reconnect(self):
		try:
			self.Connection = await create_pool(host=self._host, port=self._port,
						user=self._user, password=self._password,
						db=self._db, loop=self.Loop)
			self.ConnectionEvent.set()
		except pymysql.err.OperationalError as e:
			L.error('MySQL connection error: {}'.format(e))
			self.Loop.call_later(self._reconnect_delay, self._on_connection_error)


	def _on_connection_error(self):
		asyncio.ensure_future(self._reconnect(), loop = self.Loop)


	async def close(self):
		self.Connection.close()
		await self.Connection.wait_closed()

	
	def acquire(self):
		return self.Connection.acquire()

