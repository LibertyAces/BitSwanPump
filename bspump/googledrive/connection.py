import logging

import googleapiclient.discovery
from google.oauth2 import service_account

from ..abc.connection import Connection


L = logging.getLogger(__name__)


# https://developers.google.com/identity/protocols/OAuth2ServiceAccount

class GoogleDriveConnection(Connection):
	"""
	GoogleDriveConnection allows BSPump application to use Google Drive API.
	It can be used by connectors to take care of authentication and generate
	Google Drive service - using API v3.
	This connection is synchronous and therefore all connectors using it
	are blocking.

	To aquire service_account_file, you will need to go to console.developers.google.com and create service account.
	Create a private key for your service account and download json private key file.
	The process is well documented here https://developers.google.com/identity/protocols/OAuth2ServiceAccount .
	Then it is necessary to delegate authority over a client account to created
	service account. You can do it in admin console: https://admin.google.com/
	For more details refere to the link above.

	For the delegation, G Suite domain administrator console is necessary.
	Free Google accounts can't be used as target of Google Drive connection.
	"""

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

		svc = googleapiclient.discovery.build(
			'drive', 'v3',
			credentials=self._delegated_credentials,
			cache_discovery=False)
		return svc
