import asab
import asyncio
import logging
import asyncssh

from ..abc.source import Source

#

L = logging.getLogger(__name__)

#

ConfigDefaults = {

	'remote_path': '',
	'local_path': '',

}

class FTPSource(Source):


	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self._connection = pipeline.locate_connection(app, connection)
		self.Loop = app.Loop
		self.App = app
		self.Pipeline = pipeline

		# self._connection.PubSub.subscribe("FTPConnection.open!", self._async_connection)
		self.start(self.Loop) # without this start method, it wont run main(), I havent seen it in other sources (like amqp or mysql). Is this start method correct here?

		self._rem_path = self.Config['remote_path']
		self._loc_path = self.Config['local_path']
		self._preserve = False, #True,
		self._recurse = False, #True,


	async def main(self):
		await self._connection.ConnectionEvent.wait()
		async with self._connection.acquire_connection() as connection:#._connection_check as connection:
			async with connection.start_sftp_client() as sftp:
				await sftp.get(self._rem_path, localpath=self._loc_path, preserve=self._preserve, recurse=self._recurse)
				print('tisk')


				# try:
				# 	while True:
				# 		await self.Pipeline.ready()
				# except BaseException:
				# 	L.exception("Unexpected ssh connection error")
				# 	raise








		# 	while True:
		# 		await self.Pipeline.ready()
		# 		await sftp.get(self._fldr_name, preserve=self._preserve, recurse=self._recurse)

		# try:
		# 	while True:
		# 		# await self.Pipeline.ready() # here it doesnt go thru and it infinitely loops
		# 		# async with asyncssh.connect(
		# 		# 		host=self._connection._host,
		# 		# 		port=self._connection._port,
		# 		# 		loop=self.Loop,
		# 		# 		username=self._connection._user,
		# 		# 		password=self._connection._password,
		# 		# 		known_hosts=self._connection._known_hosts) as connection:
		# 			async with self._connection.start_sftp_client() as sftp:
		# 				await sftp.get(self._rem_path, localpath=self._loc_path, preserve=self._preserve, recurse=self._recurse)
		# 				# await self.Pipeline.ready()
		#
		# except BaseException:
		# 	L.exception("Unexpected ssh connection error")
		# 	raise

		# try: # this exception is here based on asyncssh documentation
		# 	# asyncio.get_event_loop().run_until_complete(self._async_connection())#_Should I put here async_connection method, or _conn_future?
		# except (OSError, asyncssh.Error) as exc:
		# 	sys.exit('SFTP operation failed: ' + str(exc))

		# try:
		# 	while True:
		# 		await self.Pipeline.ready()
		# 		print('jsem tady')
		# 		# connection = self._connection.result #_connection
		# 		# print(connection,'tisk')
		# 		# async with connection.start_sftp_client() as sftp:
		# 		# 	await sftp.get(self._fldr_name, preserve=self._preserve, recurse=self._recurse)
		# 		# 	print('tisk')
		#
		#
		#
		#
		# except BaseException:
		# 	L.exception("Unexpected ssh connection error")
		# 	raise

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





