import logging
import sys
import asyncio
import asyncssh
import sys

from ..abc.connection import Connection

#

L = logging.getLogger(__name__)

#

class SSHConnection(Connection):
	ConfigDefaults = {
		'host': 'localhost',
		'port': 22,
		'user': '',
		'password': '',
		'known_hosts_path': [],
		'client_host_keysign': False,
		'client_host_keys': [],
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
		self._cli_keysign = self.Config['client_host_keysign'] # if True, an attempt will be made to find ssh-keysign in its typical locations. If set to a string, that will be used as the ssh-keysign path.
		try:
			self._cli_keys = list(self.Config['client_host_keys'].split(',')) # setting the list of private / public keys when client_host_keysign = True
		except AttributeError:
			self._cli_keys = None

		# self._conn_future = None

	# 	self._on_health_check('connection.open!')
	#
	#
	#
	# def _on_health_check(self, message_type):
	# 	if self._conn_future is not None:
	# 		# Connection future exists
	#
	# 		if not self._conn_future.done():
	# 			# Connection future didn't result yet
	# 			# No sanitization needed
	# 			return
	#
	# 		try:
	# 			self._conn_future.result()
	# 		except:
	# 			# Connection future threw an error
	# 			L.exception("Unexpected connection future error")
	#
	# 		# Connection future already resulted (with or without exception)
	# 		self._conn_future = None
	#
	# 	assert (self._conn_future is None)
	#
	# 	self._conn_future = asyncio.ensure_future(
	# 		self.run_connection(),
	# 		loop=self.Loop
	# 	)


	async def run_connection(self):

		if not self._known_hosts or self._known_hosts == [''] or self._known_hosts == None:
			self._known_hosts = None
		if not self._cli_keys or self._cli_keys == [''] or self._cli_keys == None:
			self._cli_keys = None

		async with asyncssh.connect(
			host=self._host,
			port=self._port,
			loop=self.Loop,
			username=self._user,
			password=self._password,
			known_hosts=self._known_hosts,
			client_host_keysign=self._cli_keysign,
			client_host_keys=self._cli_keys,
		) as conn:
			connection = await conn
			return connection
			# chan, session = await conn.create_session(MySSHClientSession, subsystem='sftp')
			# print(chan, 'channel')
			# print(session,'session')
			# await chan.wait_closed()
			# return chan




# class MySSHClientSession(asyncssh.SSHClientSession):
# 	def connection_lost(self, exc):
# 		if exc:
# 			print('SSH session error: ' + str(exc), file=sys.stderr)

































# import logging
# import sys
# import asyncio
# import asyncssh
# import sys
#
# from ..abc.connection import Connection
#
# # import abc.connection.Connection as Connection # switch to relative path after
#
# L = logging.getLogger(__name__)
#
#
# class SshConnection(Connection):
# 	ConfigDefaults = {
# 		'host': 'test.rebex.net',#'localhost', #'itcsubmit.wustl.edu',#'localhost',
# 		'port':  22, #80,#22,  # good to use dynamic ports in range 49152-62535
# 		'user': 'demo',
# 		'password': 'password',
# 		'client_keys': [],
# 		'output_queue_max_size': 10,
# 		'known_hosts_path': [''],
#
# 		# 'process': '',
# 		# 'known_hosts': None, # None not recommended - use 'my_known_hosts' instead
# 	}
#
#
#
#
# 	def __init__(self, app, id=None, config=None):
# 		super().__init__(app, id=id, config=config)
#
# 		self.Loop = app.Loop
# 		self.PubSub = app.PubSub
#
# 		self._host = self.Config['host']
# 		self._port = self.Config['port']
# 		self._user = self.Config['user']
# 		self._password = self.Config['password']
# 		self._cli_keys = self.Config['client_keys']
# 		self._output_queue_max_size = self.Config['output_queue_max_size']
# 		self._known_hosts = self.Config['known_hosts_path']
# 		# self._options = self.Options
#
# 		# self._client_factory = self.Config['client_factory']
# 		# self._server_host = self.Config['server_host']
# 		# self._server_factory = self.Config['server_factory']
#
# 		# self._client_factory = None
# 		# self._server_factory = None
# 		# self._server_host = None
# 		#
# 		self._conn_future = None
#
# 		# self.sshClientConnection = None
# 		# self.sshClient = None
# 		# self.createServer = None
#
# 		# Subscription
# 		self._connection_check('connection.open!')
#
# 		self._output_queue = asyncio.Queue(loop=app.Loop)
#
#
# 	def _connection_check(self, message_type):
# 		if self._conn_future is not None:
# 			# Connection future exists
#
# 			if not self._conn_future.done():
# 				# Connection future didn't result yet
# 				# No sanitization needed
# 				return
#
# 			try:
# 				self._conn_future.result()
# 			except:
# 				# Connection future threw an error
# 				L.exception("Unexpected connection future error")
#
# 			# Connection future already resulted (with or without exception)
# 			self._conn_future = None
#
# 		assert (self._conn_future is None)
#
# 		self._conn_future = asyncio.ensure_future(
# 			self._async_connection(),
# 			loop=self.Loop
# 		)
#
# 		try:
# 			asyncio.get_event_loop().run_until_complete(self._conn_future)#self._async_connection())
# 		except (OSError, asyncssh.Error) as exc:
# 			sys.exit('SSH connection failed: ' + str(exc))
#
#
#
#
# 	async def _async_connection(self):
# 		try:
# 			if self._known_hosts == ['']:
# 				async with asyncssh.connect(
# 					host=self._host,
# 					port=self._port,
# 					loop=self.Loop,
# 					username=self._user,
# 					password=self._password,
# 					known_hosts = None) as connection:
# 					self._connection = connection #TODO deal with the output of connection
# 					result = await self._connection.run('echo "Hello, connection established!"', check=True)
# 					print(result.stdout, end='')
# 					# await self._loader()
#
# 					#example of piping one remote process to another
# 					# async def run_client():
# 					# 	async with asyncssh.connect('localhost') as conn:
# 					# 		proc1 = await conn.create_process(r'echo "1\n2\n3"')
# 					# 		proc2_result = await conn.run('tail -r', stdin=proc1.stdout)
# 					# 		print(proc2_result.stdout, end='')
#
#
#
#
# 			else:
# 				async with asyncssh.connect(
# 					host=self._host,
# 					port=self._port,
# 					loop=self.Loop,
# 					username=self._user,
# 					password=self._password,
# 					known_hosts = (self._known_hosts)) as connection:
# 					self._connection = connection
# 					result = await self._connection.run('echo "Hello, connection established!"', check=True)
# 					print(result.stdout, end='')
# 					# result = await self._connection.run('pwd', check=True)
# 					# print(result.stdout, end='')
#
# 					# await self._loader()
#
#
#
# 			# async def run_client():
# 			# 	async with asyncssh.connect('localhost', username='self', password='***') as conn:
# 			# 		result = await conn.run('pwd', check=True)
# 			# 		print(result.stdout, end='')
#
# 				# if self.Login != '' and self.Password != '':
# 				# 	await self.Smtp.auth_login(self.Login, self.Password)
#
# 					# asyncssh.SSHClient.validate_password(username, password)[source]
#
#
# 		except BaseException:
# 			L.exception("Unexpected ssh connection error")
# 			raise
#
#
#
#
# 	async def _loader(self):
# 		while True:
# 			bulk_out = await self._output_queue.get()
# 			print(bulk_out,'OPOPOPOPOPOPO')
# 			if bulk_out is None:
# 				break
#
# 			if self._output_queue.qsize() == self._output_queue_max_size - 1:
# 				self.PubSub.publish("SSHConnection.unpause!", self, asynchronously=True)
#
# 			 # ...
#
#
# 			#
# 			# if self._output_queue.qsize() == self._output_queue_max_size - 1:
# 			# 		self.PubSub.publish("MySQLConnection.unpause!", self, asynchronously=True)
#
# 			# async with self.acquire_connection() as connection:
# 			# 	async with connection.cursor() as cursor:
# 			# 		await cursor.executemany(query, data)
# 			# 		await connection.commit()
#
#
# # def connect(self):
# # 	loop = self.Loop  # ??
# #
# # 	self.sshClientConnection = asyncssh.connect(self._host, self._port, loop=loop)
# #
# # 	self.sshClient = asyncssh.create_connection(self._client_factory, self._host, self._port)
# #
# # 	self.createServer = asyncssh.create_server(self._server_factory, self._server_host, self._port)
# #
# # # self.clientConnSSH = asyncssh.SSHClientConnection(self._host, self._port, loop=None, self.options,
# # #                                                   acceptor=None, error_handler=None, wait=None)
# # # self.SSH.connect()
#
#
#
