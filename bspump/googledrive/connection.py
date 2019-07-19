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

		scopes = self.Config['scopes']
		service_account_file = self.Config['service_account_file']
		account_email = self.Config['account_email']

		self.ParentFolderID = self.Config['parent_folder_id']
		if self.ParentFolderID == "":
			self.ParentFolderID = None


		self.FileNameTemplate = self.Config['file_name_template']
		self.DefaultMimeType = self.Config['default_mimetype']

		self.Loop = app.Loop
		self.PubSub = app.PubSub

		self._output_queue_max_size = int(self.Config['output_queue_max_size'])
		self._output_queue = asyncio.Queue(loop=app.Loop, maxsize=self._output_queue_max_size+1)
		self.LoaderTask = asyncio.ensure_future(self._loader(), loop=self.Loop)

		self.PubSub.subscribe("Application.exit!", self._on_exit)

		self.Drive_service = self._get_service(scopes, service_account_file, account_email)


	def _get_service(self, scopes, service_account_file, account_email):
		credentials = service_account.Credentials.from_service_account_file(
			service_account_file, scopes=scopes)

		delegated_credentials = credentials.with_subject(account_email)
		svc = googleapiclient.discovery.build('drive', 'v3', credentials=delegated_credentials,cache_discovery=False)
		print("D" * 50)
		print(svc)
		print("D" * 50)
		return svc




	def consume(self, event, context):
		print("Googledrive connection consuming event..")
		self._output_queue.put_nowait((event, context))
		# print("queue len:",self._output_queue)

		if self._output_queue.qsize() == self._output_queue_max_size:
			self.PubSub.publish("GoogleDriveConnection.pause!", self)


	async def _loader(self):

		while True:
			print("_loader cycle")

			if self._output_queue.empty():
				await asyncio.sleep(5)
				continue

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
			# media = apiclient.http.MediaFileUpload(event, mimetype=mimetype)  # TODO: this should be filename
			f = io.BytesIO(event)
			media = apiclient.http.MediaIoBaseUpload(f, mimetype=mimetype)
			print("media uploaded")
			file = self.Drive_service.files().create(
				body=file_metadata,
				media_body=media,
				fields='id'
			).execute()
			print(f"File ID: {file.get('id')}")


			# if resp_text[:2].lower() != 'ok':
			# 	L.error(f"Failed to send message: {resp_text}:{smtp_response}")



	async def _on_exit(self, event_name):
		self._output_queue.put_nowait((None, None))
	# 	# Wait till the _loader() terminates
	# 	pending = [self.LoaderTask]
	# 	while len(pending) > 0:
	# 		# By sending None via queue, we signalize end of life
	# 		await self._output_queue.put(None)
	# 		done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
	# 		if self.Smtp != None:
	# 			self.Smtp.close ()