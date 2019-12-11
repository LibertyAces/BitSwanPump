import logging
import asyncio
from ..abc.sink import Sink


L = logging.getLogger(__name__)

# TODO: Research option to refactor with aiogoogle
# https://aiogoogle.readthedocs.io/en/latest/


class GoogleDriveABCSink(Sink):
	"""
	GoogleDriveABCSink is abstract class ment to be used for uploading files to GoogleDrive.
	"""
	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Drive_service = None
		self._conn_future = None
		self.Connection = pipeline.locate_connection(app, connection)
		self._output_queue = asyncio.Queue(
			loop=app.Loop,
			maxsize=self.Connection._output_queue_max_size + 1
		)

		# Subscription
		app.PubSub.subscribe("Application.stop!", self._on_exit)
		app.PubSub.subscribe("Application.tick!", self._on_health_check)
		self._on_health_check('connection.open!')


	def _on_health_check(self, message_type):
		if self._conn_future is not None:
			# Connection future exists

			if not self._conn_future.done():
				# Connection future didn't result yet
				# No sanitization needed
				return

			try:
				self._conn_future.result()
			except Exception:
				# Connection future threw an error
				L.exception("Unexpected connection future error")

			# Connection future already resulted (with or without exception)
			self._conn_future = None

		assert (self._conn_future is None)

		self._conn_future = asyncio.ensure_future(
			self._connection(),
			loop=self.Loop
		)


	async def _connection(self):
		# producer = await self.Connection.create_producer(**self._producer_params)
		if self.Drive_service is None:
			self.Drive_service = self.Connection._get_service()
		await self._loader()


	def process(self, context, event):
		self._output_queue.put_nowait((event, context))

		if self._output_queue.qsize() == self.Connection._output_queue_max_size:
			self.Pipeline.throttle(self, True)


	async def _on_exit(self, event_name, counter=None):
		self._output_queue.put_nowait((None, None))


	async def _loader(self):
		raise NotImplementedError()
