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
		'user': '',
		'password': '',
		'db': '',
		'reconnect_delay': 10.0,
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


	async def open(self):
		try:
			self.Connection = await create_pool(host=self._host, port=self._port,
						user=self._user, password=self._password,
						db=self._db, loop=self.Loop)
		except pymysql.err.OperationalError:
			# TODO: remove sleep
			await asyncio.sleep(self._reconnect_delay)
			self.Loop.create_task(self.open())


	async def close(self):
		self.Connection.close()
		await self.Connection.wait_closed()

	
	def acquire(self):
		return self.Connection.acquire()

