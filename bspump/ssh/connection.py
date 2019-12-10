import logging
import asyncio
import asyncssh

from ..abc.connection import Connection


#

L = logging.getLogger(__name__)

#


class SSHConnection(Connection):

	"""

	SSHConnection is used to connect SFTPSink to the SFTP server and upload files to the remote folder.

	SSHConnection is built on top of asyncssh library and utilizes its functions: https://asyncssh.readthedocs.io/en/latest/

	The following code illustrates how to create and register the SSH connection inside the application object.

.. code:: python


	app = bspump.BSPumpApplication()
	svc = app.get_service("bspump.PumpService")

	svc.add_connection(
		bspump.ssh.SSHConnection(app, "SSHConnection")
	)

..

	'ConfigDefaults' footnotes:

	'known_hosts'
	The list of keys which will be used to validate the server host key presented during the SSH handshake.If this is
	explicitly set to '' or None, server host key validation will be disabled.

	'client_host_keysign'
	Whether or not to use ssh-keysign to sign host-based authentication requests. If set to 'true', an attempt will be
	made to find ssh-keysign in its typical locations. If set to a string, that will be used as the ssh-keysign path.
	When set, client_host_keys should be a list of public keys. Otherwise, client_host_keys should be a list of private
	keys with optional paired certificates

	'client_host_keys'
	A list of keys to use to authenticate this client via host-based authentication. If client_host_keysign is set and no
	host keys or certificates are specified, an attempt will be made to find them in their typical locations. If
	client_host_keysign is not set, host private keys must be specified explicitly or host-based authentication will not be
	performed.

	"""

	ConfigDefaults = {

		'host': 'localhost',
		'port': 22,
		'user': '',
		'password': '',
		'known_hosts': '',  # separate paths / files with comma
		'client_host_keysign': '',  # '' -> False; 'true' -> True; 'anything_else' -> path to the directory with keys
		'client_host_keys': '',  # '' -> default. If set, separate keynames with comma

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
		# Checks void known hosts and client host keys
		if not self.Known_hosts or self.Known_hosts == [''] or self.Known_hosts is None:
			self.Known_hosts = None
		if not self.Client_keys or self.Client_keys == [''] or self.Client_keys is None:
			self.Client_keys = None
		# Sets client host keysign to boolean value. If set to path, it will try to find keysign in given path
		if self.Client_keysign != '' and self.Client_keysign != 'true':
			self.Client_keysign = str(self.Client_keysign)
		else:
			self.Client_keysign = bool(self.Client_keysign)

		conn = asyncssh.connect(
			host=self.Host,
			port=self.Port,
			username=self.User,
			password=self.Password,
			known_hosts=self.Known_hosts,
			client_host_keysign=self.Client_keysign,
			client_host_keys=self.Client_keys
		)

		return conn
