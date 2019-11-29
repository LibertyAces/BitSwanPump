import asyncio
import logging
import socket

from ..abc.sink import Sink
from ..abc.source import Source

#

L = logging.getLogger(__name__)


#


class StreamSource(Source):
	ConfigDefaults = {
		'address': '127.0.0.1:8888',  # IPv4, IPv6 or unix socket path
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Loop = app.Loop
		self.Writers = set()

		self.Address = str(self.Config['address'])

	async def handler(self, reader, writer):
		"""
		This method could be overridden to implement various application protocols.
		"""
		while True:
			await self.Pipeline.ready()
			data = await reader.readline()
			# End of stream detected
			if len(data) == 0:
				break
			await self.process(data, context={
				'peer': writer.transport.get_extra_info('peername'),
			})

	async def _handler_wrapper(self, reader, writer):
		self.Writers.add(writer)

		try:
			await self.handler(reader, writer)

		finally:
			writer.close()
			self.Writers.remove(writer)

	async def main(self):
		# Start server
		if ":" in self.Address:
			host, port = self.Address.rsplit(":", maxsplit=1)
			(family, socktype, proto, canonname, sockaddr) = socket.getaddrinfo(host, port)[0]
			host, port = sockaddr
			server = await asyncio.start_server(
				self._handler_wrapper,
				host, port,
				loop=self.Loop
			)
		else:
			server = await asyncio.start_unix_server(
				self._handler_wrapper,
				path=self.Address,
				loop=self.Loop
			)

		await self.stopped()

		# Close server
		server.close()
		await server.wait_closed()

		# Close peer connections
		for writer in self.Writers:
			L.warning("'{}' closes connection to '{}'".format(
				self.Id,
				writer.transport.get_extra_info('peername'))
			)
			if writer.can_write_eof():
				writer.write_eof()
			writer.close()


class StreamSink(Sink):
	ConfigDefaults = {
		'address': '127.0.0.1:8888',  # IPv4, IPv6 or unix socket path
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Writer = self.Reader = None
		self.Pipeline.throttle(self, enable=True)

		self.Address = str(self.Config['address'])
		self.Pipeline.PubSub.subscribe("bspump.pipeline.start!", self._open_connection)
		self.Pipeline.PubSub.subscribe("bspump.pipeline.stop!", self._close_connection)
		app.PubSub.subscribe("Application.tick!", self._health_check)

	async def _open_connection(self, message, pipeline):
		assert self.Writer is None
		if ":" in self.Address:
			host, port = self.Address.rsplit(":", maxsplit=1)
			(family, socktype, proto, canonname, sockaddr) = socket.getaddrinfo(host, port)[0]
			host, port = sockaddr
			self.Reader, self.Writer = await asyncio.open_connection(host, port)
		else:
			self.Reader, self.Writer = await asyncio.open_unix_connection(self.Address)

		pipeline.throttle(self, enable=False)

	async def _close_connection(self, message, pipeline):

		if self.Reader:
			self.Reader = None
		if self.Writer:
			self.Writer.close()
			self.Writer = None
			pipeline.throttle(self, enable=True)

		assert not self.Writer

	async def _health_check(self, message):
		if self.Reader:
			if self.Reader.at_eof():
				L.warning("Connection lost. Closing StreamSink")
				await self._close_connection(message, self.Pipeline)
		elif self.Writer is None:
			await self._open_connection(message, self.Pipeline)

	def process(self, context, event):
		self.Writer.write(event)
