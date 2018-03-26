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


	async def open(self):
		try:
			self.Connection = await create_pool(host='127.0.0.1', port=3306,
						user='root', password='root',
						db='test', loop=self.Loop)
		except pymysql.err.OperationalError:
			await asyncio.sleep(1)
			self.Loop.create_task(self._reconnect())
			return


	async def close(self):
		self.Connection.close()
		await self.Connection.wait_closed()

	
	def acquire(self):
		return self.Connection.acquire()

