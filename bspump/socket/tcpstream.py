import asyncio
from .. import Source


class _TCPStreamProtocol(asyncio.Protocol):

	#TODO: Respect pipeline is_ready

	def __init__(self, source):
		self._source = source

	def connection_made(self, transport):
		#TODO: peername = transport.get_extra_info('peername')
		self._transport = transport

	def data_received(self, data):
		message = data.decode()
		self._source.process(data)


class TCPStreamSource(Source):


	ConfigDefaults = {
		'host': '127.0.0.1',
		'port': 8888,
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Loop = app.Loop


	async def start(self):
		self._server = await self.Loop.create_server(
			lambda: _TCPStreamProtocol(self),
			self.Config['host'], int(self.Config['port'])
		)
