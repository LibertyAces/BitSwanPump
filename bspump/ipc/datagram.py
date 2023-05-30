import sys
import asyncio
import logging
import socket

from ..abc.source import Source
from ..abc.sink import Sink
from .utils import parse_address

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

		self.Address = str(self.Config['address'])
		addr_family, addr = parse_address(self.Address)

		if addr_family == socket.AF_UNIX:
			self.Socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
			self.Socket.setblocking(False)
			self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
			if self.ReceiveBufferSize > 0:
				self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.ReceiveBufferSize)

			self.Socket.bind(addr)

		else:  # Internet address family
			(family, socktype, proto, canonname, sockaddr) = socket.getaddrinfo(addr[0], addr[1])[0]
			self.Socket = socket.socket(family, socket.SOCK_DGRAM)
			self.Socket.setblocking(False)
			self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
			if self.ReceiveBufferSize > 0:
				self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.ReceiveBufferSize)

			self.Socket.bind(sockaddr)


	async def main(self):
		if sys.version_info < (3, 11):
			return await self._main_legacy()

		loop = self.Pipeline.App.Loop

		while True:
			try:
				await self.Pipeline.ready()
				event, peer = await loop.sock_recvfrom(self.Socket, self.MaxPacketSize)
				await self.Pipeline.ready()
				await self.process(event, context={'datagram': peer})

			except asyncio.CancelledError:
				break

			except Exception:
				L.exception("Error in datagram source.")
				raise


	async def _main_legacy(self):
		loop = self.Pipeline.App.Loop
		while True:
			try:
				await self.Pipeline.ready()
				event = await loop.sock_recv(self.Socket, self.MaxPacketSize)
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
