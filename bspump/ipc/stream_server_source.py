import ssl
import socket
import asyncio
import logging

from ..abc.source import Source

from .stream import Stream, TLSStream
from .protocol import LineSourceProtocol

#

L = logging.getLogger(__name__)

#


class StreamServerSource(Source):
	"""
	Description:

	"""

	ConfigDefaults = {
		'address': '127.0.0.1 8888',  # IPv4, IPv6 or unix socket path
		'backlog': '',
		# Specify 'cert' or 'key' to enable SSL / TLS mode

		# An encoding a line is going to be decoded from
		# - Pass '' (empty string) to prevent decoding
		'decode': 'utf-8',
	}

	def __init__(self, app, pipeline, id=None, config=None, protocol_class=LineSourceProtocol):
		"""
		Description:

		"""
		super().__init__(app, pipeline, id=id, config=config)

		self.Address = self.Config['address']

		if 'cert' in self.Config or 'key' in self.Config:
			import asab.net
			sslbuilder = asab.net.SSLContextBuilder('[none]', config=self.Config)
			self.SSL = sslbuilder.build(protocol=ssl.PROTOCOL_SSLv23)
		else:
			self.SSL = None

		self.AcceptingSockets = []
		self.ConnectedClients = set()  # Set of active _client_connected_task()

		self.Protocol = protocol_class(app, pipeline, config=self.Config)

		app.PubSub.subscribe("Application.tick!", self._on_tick)


	def start(self, loop):
		"""
		Description:

		"""
		if self.Task is not None:
			return

		# Create all required sockets, bind them to specific ports and start listening
		for addrline in self.Address.split('\n'):
			addrline = addrline.strip()

			if addrline.count(":") == 1:
				host, port = self.Address.rsplit(":", maxsplit=1)

				addrinfo = socket.getaddrinfo(host, port, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM, flags=socket.AI_PASSIVE)

				for family, socktype, proto, canonname, sockaddr in addrinfo:
					s = socket.socket(family, socktype, proto)
					try:
						s.bind(sockaddr)
					except OSError as e:
						L.warning("Failed to start listening at '{}': {}".format(addrline, e))
						continue

					backlog = self.Config['backlog']
					if backlog == '':
						s.listen()
					else:
						s.listen(int(backlog))

					s.setblocking(False)
					self.AcceptingSockets.append(s)


			else:
				self.Socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
				self.Socket.setblocking(False)
				self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
				self.Socket.bind(self.Address)

				L.error("Invalid address specification: '{}'".format(addrline))

		super().start(loop)


	async def stop(self):
		"""
		Description:

		"""
		# Close client connections
		for t in self.ConnectedClients:
			t.cancel()
		self.ConnectedClients = set()

		# The main() will be canceled in the parent class
		await super().stop()


	async def main(self):
		"""
		Description:

		"""
		if len(self.AcceptingSockets) == 0:
			L.error("No listening socket configured")
			return

		await asyncio.gather(
			*[
				self._handle_accept(sock)
				for sock in self.AcceptingSockets
			],
			return_exceptions=True
		)


	async def _handle_accept(self, sock):
		"""
		Description:

		"""
		loop = self.Pipeline.App.Loop
		server_addr = sock.getsockname()
		while True:
			client_sock, client_addr = await loop.sock_accept(sock)
			t = loop.create_task(
				self._client_connected_task(client_sock, client_addr, server_addr)
			)
			self.ConnectedClients.add(t)


	async def _client_connected_task(self, client_sock, client_addr, server_addr):
		"""
		Description:

		"""
		client_sock.setblocking(False)

		if client_sock.family is socket.AF_INET:
			me = '{} {}'.format(server_addr[0], server_addr[1])
			peer = '{} {}'.format(client_addr[0], client_addr[1])
		elif client_sock.family is socket.AF_INET6:
			me = '{} {}'.format(server_addr[0], server_addr[1])
			peer = '{} {}'.format(client_addr[0], client_addr[1])
		else:
			me = server_addr
			peer = client_addr

		context = {
			'stream_type': client_sock.family.name,
			'stream_dir': 'in',
			'stream_peer': peer,
			'stream_me': me,
		}
		if self.SSL is not None:
			stream = TLSStream(self.Pipeline.App.Loop, self.SSL, client_sock, server_side=True)
			ok = await stream.handshake()
			if not ok:
				return
		else:
			stream = Stream(self.Pipeline.App.Loop, client_sock)

		# This allows to send a reply to a client
		context['stream'] = stream

		inbound = self.Pipeline.App.Loop.create_task(self.Protocol.handle(self, stream, context))
		outbound = self.Pipeline.App.Loop.create_task(stream.outbound())
		done, active = await asyncio.wait(
			{inbound, outbound},
			return_when=asyncio.FIRST_COMPLETED
		)

		for t in active:
			# TODO: There could be outstanding data in the outbound queue
			#       Consider flushing them
			# Cancel remaining active tasks
			t.cancel()

		for t in done:
			try:
				await t
			except asyncio.CancelledError:
				pass
			except Exception:
				L.exception("Error when handling client socket")

		# Close the stream
		await stream.close()


	def _on_tick(self, event_name):

		# Remove clients that disconnected
		disconnected_client_tasks = [*filter(
			lambda task: task.done(),
			self.ConnectedClients
		)]
		for task in disconnected_client_tasks:
			if task.done():
				self.ConnectedClients.remove(task)

				try:
					task.result()
				except asyncio.CancelledError:
					pass
				except Exception:
					L.exception("Exception when handling client socket")
