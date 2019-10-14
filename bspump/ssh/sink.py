import asyncio
import asyncssh
import asab
import logging
import datetime
import random
import typing
import os
import re

from ..abc.sink  import Sink

#

L = logging.getLogger(__name__)

#

ConfigDefaults = {

		'remote_path': '',

		'host': 'localhost',
		'rand_int': 1000,
		'encoding': 'utf-8',
		'mode': 'w', # w = write, r = read

}

"""

If preserve is True, the access and modification times and permissions of the original file are set on the uploaded file.

If recurse is True and the remote path points at a directory, the entire subtree under that directory is uploaded.

"""

class SFTPSink(Sink):

	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self._connection = pipeline.locate_connection(app, connection)

		self._rem_path = self.Config['remote_path']
		# self._loc_path = self.Config['local_path']
		# self._preserve = bool(self.Config['preserve'])
		# self._recurse = bool(self.Config['recurse'])
		self._host = self.Config['host']
		self.RandIntLen = int(self.Config['rand_int'])
		self.Encoding = self.Config['encoding']
		self.Mode = self.Config['mode']
		self.Pipeline = pipeline

		self._output_queue = asyncio.Queue(loop=app.Loop)
		self._output_queue_max_size = 100 #int(self.Config['output_queue_max_size'])
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
		async with self._connection.run_connection() as connection: #TODO Deal with pending Task coroutine in connection
			async with connection.start_sftp_client() as sftp:
				while True:
					event, ssh_remote = await self._output_queue.get()

					if event is None and ssh_remote is None:
						break

					if self._output_queue.qsize() == self._output_queue_max_size - 1:
						self.Pipeline.throttle(self, False)

					async with sftp.open(ssh_remote, mode=self.Mode, encoding=self.Encoding) as sftpfile:
						await sftpfile.write(event)


	def process(self, context, event:typing.Union[dict, str, bytes]):
		if type(event) == bytes:
			event = event #.encode(self.Encoding)
		ssh_remote = context.get("ssh_remote", self._rem_path)

		if not os.path.isfile(ssh_remote):
			ssh_remote += str(self.file_name_generator()) # /upload/name_from_generator

		self._output_queue.put_nowait((event, ssh_remote))

		if self._output_queue.qsize() == self._output_queue_max_size:
			self.Pipeline.throttle(self, True)


	def file_name_generator(self):
		hostname = re.sub("[/,.,:, ]", "", str(self._host))
		timestamp = str(int(datetime.datetime.timestamp(datetime.datetime.now())))
		random_num = str(random.randint(1, self.RandIntLen))
		filename = str(timestamp+hostname+random_num)
		return filename
