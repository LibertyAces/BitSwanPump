import logging

import googleapiclient.discovery
from google.oauth2 import service_account

from ..abc.connection import Connection


L = logging.getLogger(__name__)


# https://developers.google.com/identity/protocols/OAuth2ServiceAccount

class GoogleDriveConnection(Connection):

	ConfigDefaults = {
		"scopes": ["https://www.googleapis.com/auth/drive"],
		'service_account_file': "",
		'account_email': "",
		'output_queue_max_size': 100
	}

	def __init__(self, app, id=None, config=None):
		super().__init__(app, id=id, config=config)

		self._scopes = self.Config['scopes']
		self._service_account_file = self.Config['service_account_file']
		self._account_email = self.Config['account_email']

		self._output_queue_max_size = int(self.Config['output_queue_max_size'])

		self._credentials = None
		self._delegated_credentials = None




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
