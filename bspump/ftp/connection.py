import logging
import sys
import asyncio
import asyncssh
import sys

from ..abc.connection import Connection

# import abc.connection.Connection as Connection # switch to relative path after

L = logging.getLogger(__name__)

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

		# Subscription
		self._connection_check('connection.open!')


	def _connection_check(self, message_type):
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

		assert (self._conn_future is None)

		self._conn_future = asyncio.ensure_future(
			self._async_connection(),
			loop=self.Loop
		)



	async def _async_connection(self):
		try:
			if not self._known_hosts or self._known_hosts == [''] or self._known_hosts == None:
				self._known_hosts = None

			async with asyncssh.connect(
					host=self._host,
					port=self._port,
					loop=self.Loop,
					username=self._user,
					password=self._password,
					known_hosts=self._known_hosts) as connection:
				self._connection = connection  # TODO deal with the output of connection
				self.ConnectionEvent.set()
				# await self._loader()

		except BaseException:
			L.exception("Unexpected ftp connection error")
			raise


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
		return asyncssh.connect(
					host=self._host,
					port=self._port,
					loop=self.Loop,
					username=self._user,
					password=self._password,
					known_hosts=self._known_hosts)


	# async def _loader(self):
	# 	while True:
	# 		rem_path, loc_path, _pres, _recur = await self._output_queue.get()
	# 		async with self.acquire_connection() as connection:
	# 			async with connection.start_sftp_client() as sftp:
	# 				await sftp.get(_rem_path, localpath=_loc_path, preserve=_pres, recurse=_recur)




