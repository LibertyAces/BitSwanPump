import asyncio
import logging
import socket

from ..abc.source import Source
from ..abc.sink import Sink

#

L = logging.getLogger(__name__)


#

class DatagramSource(Source):
	ConfigDefaults = {
		'address': '127.0.0.1:8888',  # IPv4, IPv6 or unix socket path
		'max_packet_size': 64 * 1024,
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Loop = app.Loop

		# Create a UDP socket
		self.Address = str(self.Config['address'])

		if ":" in self.Address:
			host, port = self.Address.rsplit(":", maxsplit=1)
			(family, socktype, proto, canonname, sockaddr) = socket.getaddrinfo(host, port)[0]

			self.Socket = socket.socket(family, socket.SOCK_DGRAM)
			self.Socket.setblocking(False)
			self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
			self.Socket.bind(sockaddr)

		else:

			self.Socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
			self.Socket.setblocking(False)
			self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

			self.Socket.bind(self.Address)

		self.MaxPacketSize = int(self.Config['max_packet_size'])

	async def main(self):
		task = asyncio.ensure_future(self._receive(), loop=self.Loop)

		await self.stopped()

		task.cancel()
		await task

		self.Socket.close()

	async def _receive(self):
		while True:
			try:
				await self.Pipeline.ready()
				event = await self.Loop.sock_recv(self.Socket, self.MaxPacketSize)
				await self.Pipeline.ready()
				await self.process(event)

			except asyncio.CancelledError:
				break

			except Exception:
				L.exception(f"Error in datagram source.")
				raise


class DatagramSink(Sink):
	ConfigDefaults = {
		'address': '127.0.0.1:8888',  # IPv4, IPv6 or unix socket path
		'max_packet_size': 64 * 1024,
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Loop = app.Loop

		# Create a UDP socket
		self.Address = str(self.Config['address'])

		if ":" in self.Address:
			host, port = self.Address.rsplit(":", maxsplit=1)
			(family, socktype, proto, canonname, sockaddr) = socket.getaddrinfo(host, port)[0]

			self.Socket = socket.socket(family, socket.SOCK_DGRAM)
			self.Socket.setblocking(False)
			self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
			self.Socket.connect(sockaddr)

		else:

			self.Socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
			self.Socket.setblocking(False)
			self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

			self.Socket.connect(self.Address)

		self.MaxPacketSize = int(self.Config['max_packet_size'])

	def process(self, context, event):
		self.Socket.send(event)
