import logging
import io
import asyncio
import apiclient.http

from .abcsink import GoogleDriveABCSink



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