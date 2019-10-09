import asyncio
import asyncssh
import asab
import logging

from ..abc.sink  import Sink

#

L = logging.getLogger(__name__)

#

ConfigDefaults = {

		'remote_path': '',
		'local_path': '',
		'preserve': 'False',
		'recurse': 'False',

}

class FTPSink(Sink): #TODO establish FTP sink

	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self._connection = pipeline.locate_connection(app, connection)

		self._rem_path = self.Config['remote_path']
		self._loc_path = self.Config['local_path']
		self._preserve = bool(self.Config['preserve'])
		self._recurse = bool(self.Config['recurse'])
		self.Pipeline = pipeline



		self._output_queue = asyncio.Queue(loop=app.Loop)
		self._output_queue_max_size = 100 #int(self.Config['output_queue_max_size'])
		self._conn_future = None
		# Subscription

		self._on_health_check('connection.open!')

		app.PubSub.subscribe("Application.stop!", self._on_application_stop)
		app.PubSub.subscribe("Application.tick!", self._on_health_check)



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
			self.flush(),
			loop=self.Loop
		)

	def _on_application_stop(self, message_type, counter):
		self._output_queue.put_nowait((None, None, None))


	async def flush(self):
		async with self._connection.acquire_connection() as connection:
			async with connection.start_sftp_client() as sftp:
				remote_path, local_path, recurse, preserve = await self._output_queue.get()
				if self._output_queue.qsize() == self._output_queue_max_size - 1:
					self.Pipeline.throttle(self, False)
				try:
					await sftp.mkdir(remote_path)
				except asyncssh.SFTPError:
					pass
				await sftp.put(local_path, remotepath=remote_path, preserve=preserve, recurse=recurse)



	def process(self, context, event):

		remote_path = context.get("remote_path", self._rem_path)
		local_path = context.get("local_path", self._loc_path)
		recurse = context.get("recurse", self._recurse)
		preserve = context.get("preserve", self._preserve)

		self._output_queue.put_nowait((remote_path, local_path, recurse, preserve))
		if self._output_queue.qsize() == self._output_queue_max_size:
			self.Pipeline.throttle(self, True)


