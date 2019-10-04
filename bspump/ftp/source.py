import asab
import asyncio
import logging
# import aiomysql.cursors
from ..abc.source import Source

#

L = logging.getLogger(__name__)

#

ConfigDefaults = {

	'folder_name': '',#'/pub/example/readme.txt',  # '', # can be also file name when preserve = False and recurse = False

}

# ConfigDefaults = {
# 	'host': 'test.rebex.net',  # 'localhost', #'itcsubmit.wustl.edu',#'localhost',
# 	'port': 22,  # 80,#22,  # good to use dynamic ports in range 49152-62535
# 	'user': 'demo',
# 	'password': 'password',
# 	'client_keys': [],
# 	'output_queue_max_size': 10,
# 	'known_hosts_path': [''],
# 	# 'folder_name': '/pub/example/readme.txt'#'', # can be also file name when preserve = False and recurse = False
#
# 	# 'process': '',
# 	# 'known_hosts': None, # None not recommended - use 'my_known_hosts' instead
# }

class FtpSource(Source):

	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self._connection = pipeline.locate_connection(app, connection)
		self.App = app
		 ##self.Loop = app.Loop
		# self._channel = None
		# self._channel_ready = asyncio.Event(loop=app.Loop)
		# self._channel_ready.clear()
		# self._queue = asyncio.Queue(loop=app.Loop)
		# # self._query = self.Config['query']
		#
		# self.Pipeline = pipeline
		# # self.Task = self.main()
		#
		# self._fldr_name = self.Config['folder_name']
		# #  self.Config['preserve']
		# # self.Config['recurse']
		# # self._options = self.Options
		# self._preserve = False, #True,
		# self._recurse = False, #True,
		#
		# self._connection.PubSub.subscribe("AMQPConnection.open!", self._on_connection_open)


	# def start(self, loop):
	# 	if self.Task is not None: return
	#
	# 	async def _main():
	# 		# This is to properly handle a lifecycle of the main method
	# 		try:
	# 			await self.main()
	# 		except concurrent.futures.CancelledError:
	# 			pass
	# 		except Exception as e:
	# 			self.Pipeline.set_error(None, None, e)
	# 			L.exception("Exception in the source '{}'".format(self.Id))
	#
	# 	self.Task = asyncio.ensure_future(_main(), loop=loop)
	#
	#
	#
	#
	async def main(self):

		if self._connection._connection_check.is_set() and self._channel is None:
			self._on_connection_open(".local!")

		try:
			while 1:
				await self._channel_ready.wait()
				await self.Pipeline.ready()
				async with _connection.start_sftp_client() as sftp:
					await sftp.get(self._fldr_name, preserve=self._preserve, recurse=self._recurse)

		# print('fsojfsdjfpsdj')
		# await self.Pipeline.ready()
		# # await self._simulate_event()
		# await self._connection.ConnectionEvent.wait()
		# async with self._connection.acquire_connection() as connection:
		# 	async with connection.start_sftp_client() as sftp:
		# 		await sftp.get(self._fldr_name, preserve=self._preserve, recurse=self._recurse)



		# async def run_client():
		# 	async with asyncssh.connect('localhost', username='self', password='***') as conn:
		# 		result = await conn.run('pwd', check=True)
		# 		print(result.stdout, end='')

		# if self.Login != '' and self.Password != '':
		# 	await self.Smtp.auth_login(self.Login, self.Password)

		# asyncssh.SSHClient.validate_password(username, password)[source]

		except BaseException:
			L.exception("Unexpected ssh connection error")
			raise


	def _on_connection_open(self, event_name):
		assert self._channel is None
		self._channel = self._connection.Connection.channel(on_open_callback=self._on_channel_open)
		self._channel_ready.set()

	def _on_connection_close(self, event_name):
		self._channel = None
		self._channel_ready.clear()


# import asab
# import asyncio
# import logging
# # import aiomysql.cursors
# from ..abc.source import TriggerSource
#
# #
#
# L = logging.getLogger(__name__)
#
# #
#
# ConfigDefaults = {
#
# 	'folder_name': '',#'/pub/example/readme.txt',  # '', # can be also file name when preserve = False and recurse = False
#
# }
#
# class FtpSource(TriggerSource):
#
# 	def __init__(self, app, pipeline, connection, id=None, config=None):
# 		super().__init__(app, pipeline, id=id, config=config)
# 		self.Loop = app.Loop
# 		self._connection = pipeline.locate_connection(app, connection)
# 		# self._query = self.Config['query']
# 		self.App = app
#
# 		self._fldr_name = self.Config['folder_name']
# 		#  self.Config['preserve']
# 		# self.Config['recurse']
# 		# self._options = self.Options
# 		self._preserve = False, #True,
# 		self._recurse = False, #True,
#
#
# 	async def cycle(self):
# 		await self._connection.ConnectionEvent.wait()
# 		async with self._connection.acquire_connection() as connection:
# 			async with connection.start_sftp_client() as sftp:
# 				await sftp.get(self._fldr_name, preserve=self._preserve, recurse=self._recurse)

			# async with connection.cursor(aiomysql.cursors.SSCursor) as cur:
			# 	await cur.execute(self._query)
			# 	event = {}
			# 	while True:
			# 		await self.Pipeline.ready()
			# 		row = await cur.fetchone()
			# 		if row is None:
			# 			break
			#
			# 		# Transform row to an event object
			# 		for i, val in enumerate(row):
			# 			event[cur.description[i][0]] = val
			#
			# 		# Pass event to the pipeline
			# 		await self.process(event)
			# 	await cur.execute("COMMIT;")