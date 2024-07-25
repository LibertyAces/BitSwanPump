import sys
import asyncio
import logging
import socket

import os
import stat

import asab

from ..abc.source import Source
from ..abc.sink import Sink
from .utils import parse_address, inet_family_names

#

L = logging.getLogger(__name__)


#

class DatagramSource(Source):
	"""
	Description: a datagram source that creates a UDP socket and receives datagrams.
	It is usable also with UNIX datagram sockets.
	"""


	ConfigDefaults = {
		'address': '127.0.0.1 8888',  # IPv4, IPv6 or unix socket path
		'max_packet_size': 64 * 1024,
		'receiver_buffer_size': 0,
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.ReceiveBufferSize = int(self.Config['receiver_buffer_size'])
		self.MaxPacketSize = int(self.Config['max_packet_size'])

		self.Address = self.Config['address']
		if isinstance(self.Address, int):
			self.Address = str(self.Address)

		self.AcceptingSockets = []


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

				s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
				s.setblocking(False)
				s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
				if self.ReceiveBufferSize > 0:
					s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.ReceiveBufferSize)

				s.bind(addrline)

				self.AcceptingSockets.append(s)
				L.log(asab.LOG_NOTICE, "Listening on UNIX socket (DATAGRAM)", struct_data={'path': addrline})

			else:  # Internet address family
				try:
					addrinfo = socket.getaddrinfo(addr[0], addr[1], family=socket.AF_UNSPEC, type=socket.SOCK_DGRAM, flags=socket.AI_PASSIVE)
				except Exception as e:
					L.error("Failed to open socket: {}".format(e), struct_data={'host': addr[0], 'port': addr[1]})
					continue

				for family, socktype, proto, canonname, sockaddr in addrinfo:
					s = socket.socket(family, socktype, proto)

					s.setblocking(False)
					s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
					s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
					if self.ReceiveBufferSize > 0:
						s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.ReceiveBufferSize)

					try:
						s.bind(sockaddr)
					except OSError as e:
						L.warning("Failed to start listening: {}".format(e), struct_data={'host': sockaddr[0], 'port': sockaddr[1]})
						continue

					self.AcceptingSockets.append(s)
					L.log(asab.LOG_NOTICE, "Listening on UDP", struct_data={'host': sockaddr[0], 'port': sockaddr[1], 'family': inet_family_names.get(family, "???")})


		super().start(loop)


	async def stop(self):
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
		await asyncio.gather(
			*[
				self._handle_sock_pre_311(sock) if sys.version_info < (3, 11) else self._handle_sock(sock)
				for sock in self.AcceptingSockets
			],
			return_exceptions=True
		)


	async def _handle_sock(self, sock):
		loop = self.Pipeline.App.Loop
		while True:
			try:
				await self.Pipeline.ready()
				event, peer = await loop.sock_recvfrom(sock, self.MaxPacketSize)
				await self.Pipeline.ready()
				await self.process(event, context={'datagram': peer})

			except asyncio.CancelledError:
				break

			except Exception:
				L.exception("Error in datagram source.")
				raise


	async def _handle_sock_pre_311(self, sock):
		'''
		This method provides backward compatibility with Python 3.10 and lower.

		This version doesn't send `datagram` in the context.
		'''
		loop = self.Pipeline.App.Loop
		while True:
			try:
				await self.Pipeline.ready()
				event = await loop.sock_recv(sock, self.MaxPacketSize)
				await self.process(event, context={'datagram': None})

			except asyncio.CancelledError:
				break

			except Exception:
				L.exception("Error in datagram source.")
				raise


class DatagramSink(Sink):
	"""
	Description: Outbound UDP and UNIX datagram socket.
	"""


	ConfigDefaults = {
		'address': '127.0.0.1 8888',  # IPv4, IPv6 or unix socket path
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Loop = app.Loop

		self.Address = str(self.Config['address'])
		addr_family, addr = parse_address(self.Address)


		if addr_family == socket.AF_UNIX:
			self.Socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
			self.Socket.setblocking(False)
			self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

			self.Socket.connect(addr)

		else:  # Internet address family
			(family, socktype, proto, canonname, sockaddr) = socket.getaddrinfo(addr[0], addr[1])[0]

			self.Socket = socket.socket(family, socket.SOCK_DGRAM)
			self.Socket.setblocking(False)
			self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

			self.Socket.connect(sockaddr)


	def process(self, context, event):
		self.Socket.send(event)
