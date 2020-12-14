import asyncio
import logging
import socket

from ..abc.sink import Sink

#

L = logging.getLogger(__name__)

#


class StreamClientSink(Sink):

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
