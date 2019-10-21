import logging
import asyncio
import asyncssh


from ..abc.connection import Connection


#

L = logging.getLogger(__name__)

#


"""
'known_hosts'
The list of keys which will be used to validate the server host key presented during the SSH handshake.If this is 
explicitly set to '' or None, server host key validation will be disabled. 

'client_host_keysign'
Whether or not to use ssh-keysign to sign host-based authentication requests. If set to True, an attempt will be made to 
find ssh-keysign in its typical locations. If set to a string, that will be used as the ssh-keysign path. When set, 
client_host_keys should be a list of public keys. Otherwise, client_host_keys should be a list of private keys with 
optional paired certificates

'client_host_keys'
A list of keys to use to authenticate this client via host-based authentication. If client_host_keysign is set and no 
host keys or certificates are specified, an attempt will be made to find them in their typical locations. If 
client_host_keysign is not set, host private keys must be specified explicitly or host-based authentication will not be 
performed.
"""


class SSHConnection(Connection):
	ConfigDefaults = {
		'host': 'localhost',
		'port': 22,
		'user': '',
		'password': '',
		'known_hosts': '', # separate paths / files with comma
		'client_host_keysign': '0', # True = '1', False = '0', str() = path to the directory with keys
		'client_host_keys': '', # separate keynames with comma
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
		self.Known_hosts = list(self.Config['known_hosts'].split(','))
		self.Client_keysign = self.Config['client_host_keysign']
		self.Client_keys = list(self.Config['client_host_keys'].split(','))


	def run(self):
		if not self.Known_hosts or self.Known_hosts == [''] or self.Known_hosts == None:
			self.Known_hosts = None
		if not self.Client_keys or self.Client_keys == [''] or self.Client_keys == None:
			self.Client_keys = None
		if str(self.Client_keysign).isdigit():
			self.Client_keysign = bool(int(self.Client_keysign))

		conn = asyncssh.connect(
				host=self.Host,
				port=self.Port,
				loop=self.Loop,
				username=self.User,
				password=self.Password,
				known_hosts=self.Known_hosts,
				client_host_keysign=self.Client_keysign,
				client_host_keys=self.Client_keys)

		return conn

