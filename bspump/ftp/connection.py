import logging
import aioftp
from ..abc.connection import Connection



###

L = logging.getLogger(__name__)

###


class FTPConnection(Connection):
	"""
	Description:

	|

	"""

	ConfigDefaults = {
		'hostname': 'localhost',
		'port': 21,
	}

	def __init__(self, app, id=None, config=None):
		"""
		Description:

		**Parameters**

		app : Application
			Name of the Application

		id : ID, default = None

		config : JSON, default = None

		"""
		super().__init__(app, id=id, config=config)

		self.Username = self.Config.get('username')
		self.Password = self.Config.get('password')
		self.Hostname = self.Config.get('hostname')
		self.Port = self.Config.get('port')

	async def connect(self):
		"""
		Description:

		:return: client

		|

		"""
		client = aioftp.Client()
		await client.connect(self.Hostname,21)
		await client.login(self.Username, self.Password)
		return client




