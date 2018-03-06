import asyncio
from .. import Source

class _TCPStreamProtocol(asyncio.Protocol):

	def __init__(self, source):
		self._source = source

	def connection_made(self, transport):
		peername = transport.get_extra_info('peername')
		print('Connection from {}'.format(peername))
		self._transport = transport

	def data_received(self, data):
		message = data.decode()
		self._source.process(data)


class TCPStreamSource(Source):


	def __init__(self, app, pipeline):
		super().__init__(app, pipeline)
		self.Loop = app.Loop

	async def start(self):
		self._server = await self.Loop.create_server(lambda: _TCPStreamProtocol(self), '127.0.0.1', 8888)
