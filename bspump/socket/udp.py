import logging
import socket
import asyncio
from ..abc.source import Source

#

L = logging.getLogger(__name__)

#

class UDPSource(Source):


	ConfigDefaults = {
		'host': '127.0.0.1',
		'port': 8888,
		'max_packet_size': 64*1024,
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Loop = app.Loop

		# Create a UDP socket
		self.Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.Socket.setblocking(0)
		self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
		self.Socket.bind((self.Config['host'], int(self.Config['port'])))

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
				L.exception("Error in UDP source")

