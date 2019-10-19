import asyncio
import asyncssh
import asab
import logging
import datetime
import random
import string
import typing
import os
import re

from ..abc.sink  import Sink


#

L = logging.getLogger(__name__)

#


ConfigDefaults = {

		'remote_path': '',
		'filename': 'localhost',
		'rand_int': 1000,
		'output_queue_max_size': 1000,
		'encoding': 'utf-8',
		'mode': 'w', # w = write, a = append
		'out_type': 'string'

}


class SFTPSink(Sink):

	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self._connection = pipeline.locate_connection(app, connection)

		self.RemotePath = self.Config['remote_path']
		self.fil_name = self.Config['filename']
		self.RandIntLen = int(self.Config['rand_int'])
		self.Encoding = self.Config['encoding']
		self.Mode = self.Config['mode']
		self.OutputType = self.Config['out_type']
		self.Pipeline = pipeline
		self.NameDict = {}

		self._output_queue = asyncio.Queue(loop=app.Loop)
		self._output_queue_max_size = int(self.Config['output_queue_max_size'])
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
		self.NameDict.clear()


	async def _on_exit(self, message_type):
		if self._conn_future is not None:
			await asyncio.wait([self._conn_future], return_when=asyncio.ALL_COMPLETED, loop=self.Loop)
			self.NameDict.clear()


	async def outbound(self):
		async with self._connection.run_connection() as connection:
			async with connection.start_sftp_client() as sftp:
				while True:
					event, ssh_remote = await self._output_queue.get()
					if event is None and ssh_remote is None:
						self.NameDict.clear()
						break

					if self._output_queue.qsize() == self._output_queue_max_size - 1:
						self.Pipeline.throttle(self, False)

					try:
						await sftp.mkdir(self.RemotePath) #TODO fix RuntimeError: coroutine ignored GeneratorExit when emptying queue on kill
					except asyncssh.SFTPError: #TODO explain exception https://github.com/ronf/asyncssh/issues/142
						pass

					# try:
					# 	await sftp.mkdir(self.RemotePath) #TODO fix RuntimeError: coroutine ignored GeneratorExit when emptying queue on kill
					# finally:
					# 	pass
					async with sftp.open(ssh_remote, self.Mode, encoding=self.Encoding) as sftpfile: #TODO fix RuntimeError when emptying queue on kill
						await sftpfile.write(event)


	def process(self, context, event:typing.Union[dict, str, bytes]):
		if self.OutputType == 'string':
			if type(event) == str:
				event = event
			elif type(event) == bytes:
				event = event.decode(self.Encoding)
		elif self.OutputType == 'bytes':
			if type(event) == str:
				event = event.encode(self.Encoding)
			elif type(event) == bytes:
				event = event

		ssh_remote = context.get("ssh_remote", self.RemotePath)

		if not os.path.isfile(ssh_remote):
			# It will create the path of a file: /RemotePath/name_from_builder
			ssh_remote += str(self.build_remote_file_name())

		self._output_queue.put_nowait((event, ssh_remote))

		if self._output_queue.qsize() == self._output_queue_max_size:
			self.Pipeline.throttle(self, True)


	def build_remote_file_name(self):
		hostname = re.sub("[/,.,:, ]", "", str(self.fil_name))
		timestamp = str(int(datetime.datetime.timestamp(datetime.datetime.now())))
		random_num = str(random.randint(1, self.RandIntLen))
		filename = str(timestamp+hostname+random_num)

		if filename not in self.NameDict:
			self.NameDict[filename] = 'id' + ' ' + random_num
		else:
			filename = filename + str(random.choice(string.ascii_letters))
			self.NameDict[filename] = 'id' + ' ' + random_num

		return filename

