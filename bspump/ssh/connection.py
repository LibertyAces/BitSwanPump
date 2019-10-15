import logging
import sys
import asyncio
import asyncssh
import sys

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

		self._host = self.Config['host']
		self._port = int(self.Config['port'])
		self._user = self.Config['user']
		self._password = self.Config['password']
		try:
			self._known_hosts = list(self.Config['known_hosts_path'].split(','))
		except AttributeError:
			self._known_hosts = None
		self._cli_keysign = self.Config['client_host_keysign'] # if True, an attempt will be made to find ssh-keysign in its typical locations. If set to a string, that will be used as the ssh-keysign path.
		try:
			self._cli_keys = list(self.Config['client_host_keys'].split(',')) # setting the list of private / public keys when client_host_keysign = True
		except AttributeError:
			self._cli_keys = None


	def run_connection(self):

		if not self._known_hosts or self._known_hosts == [''] or self._known_hosts == None:
			self._known_hosts = None
		if not self._cli_keys or self._cli_keys == [''] or self._cli_keys == None:
			self._cli_keys = None

		conn = asyncssh.connect(
				host=self._host,
				port=self._port,
				loop=self.Loop,
				username=self._user,
				password=self._password,
				known_hosts=self._known_hosts,
				client_host_keysign=self._cli_keysign,
				client_host_keys=self._cli_keys)

		return conn

