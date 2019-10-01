import logging
import sys
import asyncio
import asyncssh
import sys

from ..abc.connection import Connection

# import abc.connection.Connection as Connection # switch to relative path after

L = logging.getLogger(__name__)


class SshConnection(Connection):
	ConfigDefaults = {
		'host': 'localhost',
		'port': 22,  # good to use dynamic ports in range 49152-62535
		'user': '',
		'password': '',
		'client_keys': '',

		# 'process': '',
		# 'known_hosts': None, # None not recommended - use 'my_known_hosts' instead
	}

	#
	# options = {
	#     'known_hosts': '',
	#     'server_host_key_algs': '',
	#     'username': '',
	#     'password': '',
	# }

	def __init__(self, app, id=None, config=None):
		super().__init__(app, id=id, config=config)

		self.Loop = app.Loop
		self.PubSub = app.PubSub

		self._host = self.Config['host']
		self._port = self.Config['port']
		# self._client_factory = self.Config['client_factory']
		# self._server_host = self.Config['server_host']
		# self._server_factory = self.Config['server_factory']

		self._client_factory = None
		self._server_factory = None
		self._server_host = None

		self._conn_future = None

		# self.sshClientConnection = None
		# self.sshClient = None
		# self.createServer = None

		# Subscription
		self._connection_check('connection.open!')

		self._output_queue = asyncio.Queue(loop=app.Loop)


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
			async with asyncssh.connect(
				host=self._host,
				port=self._port,
				loop=self.Loop) as connection:
				self._connection = connection

		except BaseException:
			L.exception("Unexpected ssh connection error")
			raise


# def connect(self):
# 	loop = self.Loop  # ??
#
# 	self.sshClientConnection = asyncssh.connect(self._host, self._port, loop=loop)
#
# 	self.sshClient = asyncssh.create_connection(self._client_factory, self._host, self._port)
#
# 	self.createServer = asyncssh.create_server(self._server_factory, self._server_host, self._port)
#
# # self.clientConnSSH = asyncssh.SSHClientConnection(self._host, self._port, loop=None, self.options,
# #                                                   acceptor=None, error_handler=None, wait=None)
# # self.SSH.connect()


class SftpConnection(Connection):
	...

# ConfigDefaults = {
#     'host': 'localhost',
#     'port': 8022, # good to use dynamic ports in range 49152-62535
#     # 'user': '',
#     # 'password': '',
#     'client_keys': '',
#     'process': '',
#     'known_hosts': None, # None not recommended - use 'my_known_hosts' instead
#     'use_preserve': False,
#     'use_recurse': False,
#     'file': '',
#
#
# }
#
#
# def __init__(self, app, id=None, config=None):
#     super().__init__(app, id=id, config=config)
#
#     self._host = self.Config['host']
#     self._port = self.Config['port']
#
#     self._file = self.Config['file']
#     self._preserve = self.Config['use_preserve']
#     self._recurse = self.Config['use_recurse']

# async def start_server():
#     await asyncssh.listen(self._host, self._port, server_host_keys=['ssh_host_key'],
#                           authorized_client_keys='ssh_user_ca',
#                           sftp_factory=True)
#
# loop = asyncio.get_event_loop()
#
# try:
#     loop.run_until_complete(start_server())
# except (OSError, asyncssh.Error) as exc:
#     sys.exit('Error starting server: ' + str(exc))
#
# loop.run_forever()

# def __init__(self, app, id=None, config=None):
#     super().__init__(app, id=id, config=config)
#
#     self._host = self.Config['host']
#
#     self._file = self.Config['file']
#     self._preserve = self.Config['use_preserve']
#     self._recurse = self.Config['use_recurse']
#
#
#
# async def run_client():
#     async with asyncssh.connect('localhost') as conn:
#         async with conn.start_sftp_client() as sftp:
#             await sftp.get(self._file, self._preserve, self._recurse)
#
# try:
#     asyncio.get_event_loop().run_until_complete(run_client())
# except (OSError, asyncssh.Error) as exc:
#     sys.exit('SFTP operation failed: ' + str(exc))
