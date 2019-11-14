import asyncio
import logging
import socket

from ..abc.source import Source

#

L = logging.getLogger(__name__)


#

class DatagramSource(Source):
	ConfigDefaults = {
		'host': '127.0.0.1',
		'port': 8888,
		'socket_path': '',
		'max_packet_size': 64 * 1024,
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Loop = app.Loop

		# Create a UDP socket
		self.Host = self.Config['host']
		self.Port = int(self.Config['port']) if self.Config['port'] else None
		self.SocketPath = self.Config['socket_path']

		family = socket.AF_UNIX if self.SocketPath else socket.AF_INET

		self.Socket = socket.socket(family, socket.SOCK_DGRAM)
		self.Socket.setblocking(False)
		self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
		if self.SocketPath:
			self.Socket.bind(self.SocketPath)
		else:
			self.Socket.bind((self.Host, self.Port))

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

			except Exception as e:
				L.exception(f"Error in UDP source. {e}")
				raise
