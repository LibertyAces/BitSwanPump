import logging
import asyncio
import io
import googleapiclient.discovery
import apiclient.http
from google.oauth2 import service_account

from ..abc.connection import Connection


L = logging.getLogger(__name__)


# https://developers.google.com/identity/protocols/OAuth2ServiceAccount

class GoogleDriveConnection(Connection):

	ConfigDefaults = {
		"scopes": ["https://www.googleapis.com/auth/drive"],
		'service_account_file': "",
		'account_email': "",
		'parent_folder_id': "",
		'file_name_template': "",
		'default_mimetype': "",

		'output_queue_max_size': 100
	}

	def __init__(self, app, id=None, config=None):
		super().__init__(app, id=id, config=config)

		self._scopes = self.Config['scopes']
		self._service_account_file = self.Config['service_account_file']
		self._account_email = self.Config['account_email']

		self.ParentFolderID = self.Config['parent_folder_id']
		if self.ParentFolderID == "":
			self.ParentFolderID = None


		self.FileNameTemplate = self.Config['file_name_template']
		self.DefaultMimeType = self.Config['default_mimetype']

		self.Loop = app.Loop
		self.PubSub = app.PubSub

		self._output_queue_max_size = int(self.Config['output_queue_max_size'])
		self._output_queue = asyncio.Queue(loop=app.Loop, maxsize=self._output_queue_max_size+1)
		# self.LoaderTask = asyncio.ensure_future(self._loader(), loop=self.Loop)
		self._conn_future = None
		self._credentials = None
		self._delegated_credentials = None

		app.PubSub.subscribe("Application.stop!", self._on_exit)
		app.PubSub.subscribe("Application.tick!", self._on_health_check)
		self._on_health_check('connection.open!')



	def _get_service(self):
		if self._credentials is None:
			self._credentials = service_account.Credentials.from_service_account_file(
				self._service_account_file, scopes=self._scopes)

		if self._delegated_credentials is None:
			self._delegated_credentials = self._credentials.with_subject(self._account_email)

		svc = googleapiclient.discovery.build('drive', 'v3',
											  credentials=self._delegated_credentials,
											  cache_discovery=False)
		return svc



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
		self.Drive_service = self._get_service()
		await self._loader ()


	async def _loader(self):
		while True:
			print("_loader cycle")

			event, context = await self._output_queue.get()
			print("loader got event with context:",context)
			if event is None:
				print("_loader break")
				break

			context_mimetype = context.get('mimetype')
			if context_mimetype is not None:
				mimetype =  context_mimetype
			else:
				mimetype = self.DefaultMimeType

			context_filename = context.get('filename')
			if context_filename is not None:
				filename = context_filename
			else:
				filename = self.FileNameTemplate


			if self._output_queue.qsize() == self._output_queue_max_size - 1:
				self.PubSub.publish("GoogleDriveConnection.unpause!", self, asynchronously=True)

			file_metadata = {
				'name': filename,
				'parents': self.ParentFolderID
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
			print(f"File ID: {drive_file.get('id')}")

			# if resp_text[:2].lower() != 'ok':
			# 	L.error(f"Failed to send message: {resp_text}:{smtp_response}")


	def consume(self, event, context):
		print("Googledrive connection consuming event..")
		self._output_queue.put_nowait((event, context))
		# print("queue len:",self._output_queue)

		if self._output_queue.qsize() == self._output_queue_max_size:
			self.PubSub.publish("GoogleDriveConnection.pause!", self)


	async def _on_exit(self, event_name, counter= None):
		self._output_queue.put_nowait((None, None))