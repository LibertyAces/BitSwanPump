import logging
import sys
import asyncio
import asyncssh
import sys

from ..abc.connection import Connection

#

L = logging.getLogger(__name__)

#

class FTPConnection(Connection):
	ConfigDefaults = {
		'host': 'localhost',
		'port': 22,
		'user': '',
		'password': '',
		'known_hosts_path': [],
	}

	def __init__(self, app, id=None, config=None):
		super().__init__(app, id=id, config=config)

		self.ConnectionEvent = asyncio.Event(loop=app.Loop)
		self.ConnectionEvent.clear()

		self.Loop = app.Loop

		self._host = self.Config['host']
		self._port = int(self.Config['port'])
		self._user = self.Config['user']
		self._password = self.Config['password']
		try:
			self._known_hosts = list(self.Config['known_hosts_path'].split(','))
		except AttributeError:
			self._known_hosts = None

		self._conn_future = None


	def acquire_connection(self):
		"""
		Acquire asynchronous database connection

		Use with `async with` statement

	.. code-block:: python

		async with self.Connection.acquire_connection() as connection:
			async with connection.start_sftp_client() as sftp:
				await sftp.get(self._rem_path, localpath=self._loc_path, preserve=self._preserve, recurse=self._recurse)

		:return: Asynchronous Context Manager
		"""
		try:
			if not self._known_hosts or self._known_hosts == [''] or self._known_hosts == None:
				self._known_hosts = None

			self._connection = asyncssh.connect(
				host=self._host,
				port=self._port,
				loop=self.Loop,
				username=self._user,
				password=self._password,
				known_hosts=self._known_hosts)

		except BaseException:
			L.exception("Unexpected ftp connection error")
			raise

		return self._connection
