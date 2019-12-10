import logging
import io
import apiclient.http
from .abcsink import GoogleDriveABCSink


L = logging.getLogger(__name__)


class GoogleDriveBlockSink(GoogleDriveABCSink):
	"""
		GoogleDriveBlockSink is a file sink processor that can be used to upload individual
		events as files to Google drive using GoogleDriveConnection.
		Properties `filename` and 'mimetype' from event context are used as metadata.
		If they are not present, default from configuration is used instead.
		"""
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
		self.DefaultFilename = self.Config['default_filename']
		self.DefaultMimeType = self.Config['default_mimetype']


	async def _loader(self):
		while True:
			event, context = await self._output_queue.get()

			if event is None:
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
			file = io.BytesIO(event)
			media = apiclient.http.MediaIoBaseUpload(file, mimetype=mimetype, resumable=True)
			drive_file = self.Drive_service.files().create(
				body=file_metadata,
				media_body=media,
				fields='id'
			).execute()

			if drive_file.get('id') is None:
				L.error(f"Failed upload file to Google drive: {file_metadata['name']}")
