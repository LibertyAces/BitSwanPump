import logging
import io
import asyncio
import apiclient.http
from ..abc.sink import Sink


L = logging.getLogger(__name__)

# TODO: Research option to refactor to aiogoogle
# https://aiogoogle.readthedocs.io/en/latest/

class GoogleDriveABCSink(Sink):

	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Drive_service = None
		self._conn_future = None
		self.Connection = pipeline.locate_connection(app, connection)
		self._output_queue = asyncio.Queue(loop=app.Loop,
										   maxsize=self.Connection._output_queue_max_size + 1)

		# Subscription
		app.PubSub.subscribe("Application.stop!", self._on_exit)
		app.PubSub.subscribe("Application.tick!", self._on_health_check)
		self._on_health_check('connection.open!')


	def _on_health_check(self, message_type):
		print('_on_health_check')
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
			self._connection(),
			loop=self.Loop
		)


	async def _connection(self):
		# producer = await self.Connection.create_producer(**self._producer_params)
		if self.Drive_service is None:
			self.Drive_service = self.Connection._get_service()
		await self._loader ()


	def process(self, context, event):
		print("Googledrive sink processing event..")
		self._output_queue.put_nowait((event, context))
		# print("queue len:",self._output_queue)

		if self._output_queue.qsize() == self.Connection._output_queue_max_size:
			self.Pipeline.throttle(self, True)


	async def _on_exit(self, event_name, counter= None):
		self._output_queue.put_nowait((None, None))


	async def _loader(self):
		raise NotImplemented()



class GoogleDriveBlockSink(GoogleDriveABCSink):

	ConfigDefaults = {
		'parent_folder_id': "",
		'default_filename': "untitled_file",
		'default_mimetype': "",
	}

	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, connection, id=id, config=config)

		self.ParentFolderID = self.Config['parent_folder_id']
		if self.ParentFolderID == "":
			self.ParentFolderID = None
		print("|" * 30, "self.ParentFolderID", self.ParentFolderID)
		self.DefaultFilename = self.Config['default_filename']
		self.DefaultMimeType = self.Config['default_mimetype']


	async def _loader(self):
		while True:
			print("_loader cycle")
			event, context = await self._output_queue.get()
			print("loader got event with context:",context)

			if event is None:
				print("_loader break")
				break

			ctx_mime = context.get('mimetype')
			mimetype = ctx_mime if ctx_mime is not None else self.DefaultMimeType

			ctx_fn = context.get('filename')
			filename = ctx_fn if ctx_fn is not None else self.DefaultFilename


			if self._output_queue.qsize() == self.Connection._output_queue_max_size - 1:
				self.Pipeline.throttle(self, False)

			file_metadata = {
				'name': filename,
				'parents': [self.ParentFolderID]
			}
			print("="*30,file_metadata)
			file = io.BytesIO(event)
			media = apiclient.http.MediaIoBaseUpload(file, mimetype=mimetype)
			print("media uploaded")
			drive_file = self.Drive_service.files().create(
				body=file_metadata,
				media_body=media,
				fields='id'
			).execute()

			if drive_file.get('id') is None:
				L.error(f"Failed upload file to Google drive: {file_metadata['name']}")
			else:
				print(f"File ID: {drive_file.get('id')}")