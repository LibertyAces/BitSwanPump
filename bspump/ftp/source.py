import asab
import asyncio
import logging
import asyncssh

# import aiomysql.cursors
from ..abc.source import Source

#

L = logging.getLogger(__name__)

#

ConfigDefaults = {

	'folder_name': '',
	# '/pub/example/readme.txt',  # '', # can be also file name when preserve = False and recurse = False

}

class FTPSource(Source):


	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self._connection = pipeline.locate_connection(app, connection)
		self.Loop = app.Loop
		self.App = app
		self.Pipeline = pipeline

		# self._connection.PubSub.subscribe("FTPConnection.open!", self._async_connection)
		self.start(self.Loop)

		self._fldr_name = self.Config['folder_name']
		self._preserve = False, #True,
		self._recurse = False, #True,


	async def main(self):
		await self._connection.ConnectionEvent.wait()
		# async with self._connection as connection:#._connection_check as connection:
		# async with self._connection.start_sftp_client() as sftp:
		# 	while True:
		# 		await self.Pipeline.ready()
		# 		await sftp.get(self._fldr_name, preserve=self._preserve, recurse=self._recurse)
		try:
			while True:
				await self.Pipeline.ready()
				connection = self._connection._connection
				async with connection.start_sftp_client() as sftp:
					await sftp.get(self._fldr_name, preserve=self._preserve, recurse=self._recurse)
					print('tisk')




		except BaseException:
			L.exception("Unexpected ssh connection error")
			raise

		# try:
		# 	while True:
		# 		# await self._channel_ready.wait()
		# 		print('predpipe')
		# 		print(self.Pipeline)
		# 		if self.Pipeline == True:
		# 			print('pp True')
		# 		else:
		# 			print('pp False')
		# 		await self.Pipeline.ready()
		# 		print('pipeline ready')
		# 		print(self._connection)
		# 		# async with self._connection:
		# 		async with self._connection.start_sftp_client() as sftp:
		# 			await sftp.get(self._fldr_name, preserve=self._preserve, recurse=self._recurse)
		# 			print('vytisknuto')
		#
		#
		# except BaseException:
		# 	L.exception("Unexpected ssh connection error")
		# 	raise


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