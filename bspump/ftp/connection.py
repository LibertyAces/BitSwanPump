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
		'host': 'test.rebex.net',  # 'localhost', #'itcsubmit.wustl.edu',#'localhost',
		'port': 22,  # 80,#22,  # good to use dynamic ports in range 49152-62535
		'user': 'demo',
		'password': 'password',
		'client_keys': [],
		'output_queue_max_size': 10,
		'known_hosts_path': [''],
		'folder_name': '/pub/example/readme.txt'#'', # can be also file name when preserve = False and recurse = False


		# 'process': '',
		# 'known_hosts': None, # None not recommended - use 'my_known_hosts' instead
	}

	def __init__(self, app, id=None, config=None):
		super().__init__(app, id=id, config=config)

		self.ConnectionEvent = asyncio.Event(loop=app.Loop)
		self.ConnectionEvent.clear()

		self.Loop = app.Loop
		self.PubSub = app.PubSub

		self._host = self.Config['host']
		self._port = self.Config['port']
		self._user = self.Config['user']
		self._password = self.Config['password']
		self._cli_keys = self.Config['client_keys']
		self._output_queue_max_size = self.Config['output_queue_max_size']
		self._known_hosts = self.Config['known_hosts_path']
		# self._fldr_name = self.Config['folder_name']
		# self._preserve = False, #True,
		# self._recurse = False, #True,

		self._conn_future = None



		# Subscription
		self._connection_check('connection.open!')
		# self._output_queue = asyncio.Queue(loop=app.Loop)


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

		try:
			asyncio.get_event_loop().run_until_complete(self._async_connection())#_conn_future)  #return?
			self.ConnectionEvent.set()
		except (OSError, asyncssh.Error) as exc:
			sys.exit('SFTP operation failed: ' + str(exc))

	async def _async_connection(self):
		try:
			if self._known_hosts == ['']:
				async with asyncssh.connect(
						host=self._host,
						port=self._port,
						loop=self.Loop,
						username=self._user,
						password=self._password,
						known_hosts=None) as connection:
					self._connection = connection  # TODO deal with the output of connection
					# self.ConnectionEvent.set()

					# return self._connection # ? TODO

					# async with self._connection.start_sftp_client() as sftp:
					# 	self.result = await sftp.get(self._fldr_name, preserve=self._preserve, recurse=self._recurse)
					# 	return self.result

					# result = await self.run('echo "Hello, connection established!"', check=True)
					# return result
					# print(result.stdout, end='')
			# await self._loader()

			# example of piping one remote process to another
			# async def run_client():
			# 	async with asyncssh.connect('localhost') as conn:
			# 		proc1 = await conn.create_process(r'echo "1\n2\n3"')
			# 		proc2_result = await conn.run('tail -r', stdin=proc1.stdout)
			# 		print(proc2_result.stdout, end='')




			else:
				async with asyncssh.connect(
						host=self._host,
						port=self._port,
						loop=self.Loop,
						username=self._user,
						password=self._password,
						known_hosts=(self._known_hosts)) as connection:
					self._connection = connection
					self._connection = connection  # TODO deal with the output of connection
					self.ConnectionEvent.set()
					# result = await self._connection.run('echo "Hello, connection established!"', check=True)
					# return result
					# print(result.stdout, end='')
			# result = await self._connection.run('pwd', check=True)
			# print(result.stdout, end='')

			# await self._loader()

		except BaseException:
			L.exception("Unexpected ftp connection error")
			raise

