import os
import stat
import ssl
import socket
import asyncio
import logging

import asab

from ..abc.source import Source

from .stream import Stream, TLSStream
from .protocol import LineSourceProtocol
from .utils import parse_address, inet_family_names

#

L = logging.getLogger(__name__)

#


class StreamServerSource(Source):

	ConfigDefaults = {
		'address': '127.0.0.1 8888',  # IPv4, IPv6 or unix socket path
		'backlog': '',
		# Specify 'cert' or 'key' to enable SSL / TLS mode

		# An encoding a line is going to be decoded from
		# - Pass '' (empty string) to prevent decoding
		'decode': 'utf-8',
	}

	def __init__(self, app, pipeline, id=None, config=None, protocol_class=LineSourceProtocol):
		super().__init__(app, pipeline, id=id, config=config)

		self.Address = self.Config['address']
		if isinstance(self.Address, int):
			self.Address = str(self.Address)

		if 'cert' in self.Config or 'key' in self.Config:
			import asab.tls
			sslbuilder = asab.tls.SSLContextBuilder('[none]', config=self.Config)
			self.SSL = sslbuilder.build(protocol=ssl.PROTOCOL_SSLv23)
		else:
			self.SSL = None

		self.AcceptingSockets = []
		self.ConnectedClients = set()  # Set of active _client_connected_task()

		self.Protocol = protocol_class(app, pipeline, config=self.Config)

		app.PubSub.subscribe("Application.tick!", self._on_tick)


	def start(self, loop):
		if self.Task is not None:
			return

		# Create all required sockets, bind them to specific ports and start listening
		for addrline in self.Address.split('\n'):
			addrline = addrline.strip()
			addr_family, addr = parse_address(self.Address)

			if addr_family == socket.AF_UNIX:

				if os.path.exists(addrline):
					usstat = os.stat(addrline)
					if stat.S_ISSOCK(usstat.st_mode):
						os.unlink(addrline)
					else:
						L.warn("Cannot listen on UNIX socket, path is already occupied", struct_data={'path': addrline})
						continue

				s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
				s.setblocking(False)
				s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
				s.bind(addrline)

				self.AcceptingSockets.append(s)
				L.log(asab.LOG_NOTICE, "Listening on UNIX socket (STREAM)", struct_data={'path': addrline})

			else:  # Internet address family
				try:
					addrinfo = socket.getaddrinfo(addr[0], addr[1], family=socket.AF_UNSPEC, type=socket.SOCK_STREAM, flags=socket.AI_PASSIVE)
				except Exception as e:
					L.error("Failed to open socket: {}".format(e), struct_data={'host': addr[0], 'port': addr[1]})
					continue

				for family, socktype, proto, canonname, sockaddr in addrinfo:
					s = socket.socket(family, socktype, proto)

					s.setblocking(False)
					s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
					s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

					try:
						s.bind(sockaddr)
					except OSError as e:
						L.warning("Failed to start listening: {}".format(e), struct_data={'host': sockaddr[0], 'port': sockaddr[1]})
						continue

					backlog = self.Config['backlog']
					if backlog == '':
						s.listen()
					else:
						s.listen(int(backlog))

					self.AcceptingSockets.append(s)
					L.log(asab.LOG_NOTICE, "Listening on TCP", struct_data={'host': sockaddr[0], 'port': sockaddr[1], 'family': inet_family_names.get(family, "???")})


		super().start(loop)


	async def stop(self):
		# Close client connections
		for t in self.ConnectedClients:
			t.cancel()
		self.ConnectedClients = set()

		for s in self.AcceptingSockets:
			if s.family == socket.AF_UNIX:
				# We should remove the UNIX socket when the the collector is not running
				try:
					os.unlink(s.getsockname())
				except Exception:
					L.exception("Error when removing socket file")

		# The main() will be canceled in the parent class
		await super().stop()


	async def main(self):
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
		loop = self.Pipeline.App.Loop
		server_addr = sock.getsockname()
		while True:
			client_sock, client_addr = await loop.sock_accept(sock)
			t = loop.create_task(
				self._client_connected_task(client_sock, client_addr, server_addr)
			)
			self.ConnectedClients.add(t)


	async def _client_connected_task(self, client_sock, client_addr, server_addr):
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

		L.log(asab.LOG_NOTICE, "Connected.", struct_data={'peer': peer})

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

		L.log(asab.LOG_NOTICE, "Disconnected.", struct_data={'peer': peer})

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
