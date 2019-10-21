import asyncio
import asyncssh
import asab
import logging
import datetime
import random
import string
import typing
import re

from ..abc.sink  import Sink


#

L = logging.getLogger(__name__)

#


ConfigDefaults = {

		'remote_path': '',
		'filename': 'localhost',
		'mode': 'w', # w = write, a = append

}


class SFTPSink(Sink):

	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Connection = pipeline.locate_connection(app, connection)

		self.RemotePath = self.Config['remote_path']
		self.File_name = self.Config['filename']
		self.RandIntLen = 1000
		self.Mode = self.Config['mode']
		self.Pipeline = pipeline

		self._output_queue = asyncio.Queue(loop=app.Loop)
		self._output_queue_max_size = 1000
		self._conn_future = None

		# Subscription
		self._on_health_check('connection.open!')

		app.PubSub.subscribe("Application.stop!", self._on_application_stop)
		app.PubSub.subscribe("Application.tick!", self._on_health_check)
		app.PubSub.subscribe("Application.exit!", self._on_exit)


	def _on_health_check(self, message_type):
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
			self.outbound(),
			loop=self.Loop
		)


	def _on_application_stop(self, message_type, counter):
		self._output_queue.put_nowait((None, None))


	async def _on_exit(self, message_type):
		if self._conn_future is not None:
			await asyncio.wait([self._conn_future], return_when=asyncio.ALL_COMPLETED, loop=self.Loop)


	async def outbound(self):
		async with self.Connection.run() as connection:
			async with connection.start_sftp_client() as sftp:
				while True:
					event, ssh_remote = await self._output_queue.get()

					if event is None and ssh_remote is None:
						break

					if self._output_queue.qsize() == self._output_queue_max_size - 1:
						self.Pipeline.throttle(self, False)
					# Create folder on remote path if does not exist yet
					try:
						await sftp.mkdir(self.RemotePath) #TODO fix RuntimeError: coroutine ignored GeneratorExit when emptying queue on kill
					except asyncssh.SFTPError:
						pass
					# Checks if the file of given name already exists on remote folder
					try:
						while True:
							if await sftp.exists(ssh_remote):
								ssh_remote = ssh_remote + "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
							else:
								ssh_remote = ssh_remote
								break
					except asyncssh.SFTPError:
						pass
					# Writes event into a remote file
					async with sftp.open(ssh_remote, self.Mode, encoding=None) as sftpfile: #TODO fix RuntimeError when emptying queue on kill
						await sftpfile.write(event)


	def process(self, context, event:typing.Union[dict, str, bytes]):
		if type(event) == str:
			event = event.encode('utf-8')
		elif type(event) == bytes:
			event = event

		ssh_remote = context.get("ssh_remote", self.RemotePath)
		# It will create the path of a file: /RemotePath/name_from_builder
		ssh_remote += str(self.build_remote_file_name())

		self._output_queue.put_nowait((event, ssh_remote))

		if self._output_queue.qsize() == self._output_queue_max_size:
			self.Pipeline.throttle(self, True)


	def build_remote_file_name(self):
		hostname = re.sub("[/,.,:, ]", "", str(self.File_name))
		timestamp = str(int(datetime.datetime.timestamp(datetime.datetime.now())))
		random_num = str(random.randint(1, self.RandIntLen))
		filename = str(timestamp+hostname+random_num)

		return filename

