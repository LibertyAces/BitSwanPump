import logging
import aioftp
from ..abc.connection import Connection



###

L = logging.getLogger(__name__)

###


class FTPConnection(Connection):

	ConfigDefaults = {
		'hostname': 'localhost',
		'port': 21,
	}

	def __init__(self, app, id=None, config=None):
		super().__init__(app, id=id, config=config)

		self.Username = self.Config.get('username')
		self.Password = self.Config.get('password')
		self.Hostname = self.Config.get('hostname')
		self.Port = self.Config.get('port')

	async def connect(self):
		client = aioftp.Client()
		await client.connect(self.Hostname,21)
		await client.login(self.Username, self.Password)
		return client




