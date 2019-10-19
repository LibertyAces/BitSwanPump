import logging
import asyncio
import asyncssh


from ..abc.connection import Connection


#

L = logging.getLogger(__name__)

#


class SSHConnection(Connection):
	ConfigDefaults = {
		'host': 'localhost',
		'port': 22,
		'user': '',
		'password': '',
		'known_hosts_path': [],
		'client_host_keysign': False,
		'client_host_keys': [],
	}

	def __init__(self, app, id=None, config=None):
		super().__init__(app, id=id, config=config)

		self.ConnectionEvent = asyncio.Event(loop=app.Loop)
		self.ConnectionEvent.clear()

		self.Loop = app.Loop

		self.Host = self.Config['host']
		self.Port = int(self.Config['port'])
		self.User = self.Config['user']
		self.Password = self.Config['password']
		try:
			self.Known_hosts = list(self.Config['known_hosts_path'].split(','))
		except AttributeError:
			self.Known_hosts = None
		self.Cli_keysign = self.Config['client_host_keysign'] # if True, an attempt will be made to find ssh-keysign in its typical locations. If set to a string, that will be used as the ssh-keysign path.
		try:
			self.Cli_keys = list(self.Config['client_host_keys'].split(',')) # setting the list of private / public keys when client_host_keysign = True
		except AttributeError:
			self.Cli_keys = None


	def run_connection(self):

		if not self.Known_hosts or self.Known_hosts == [''] or self.Known_hosts == None:
			self.Known_hosts = None
		if not self.Cli_keys or self.Cli_keys == [''] or self.Cli_keys == None:
			self.Cli_keys = None

		conn = asyncssh.connect(
				host=self.Host,
				port=self.Port,
				loop=self.Loop,
				username=self.User,
				password=self.Password,
				known_hosts=self.Known_hosts,
				client_host_keysign=self.Cli_keysign,
				client_host_keys=self.Cli_keys)

		return conn

