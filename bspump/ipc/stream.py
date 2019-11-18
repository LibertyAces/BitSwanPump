import asyncio
import logging

from ..abc.source import Source

#

L = logging.getLogger(__name__)


#


class StreamSource(Source):
	ConfigDefaults = {
		'host': '127.0.0.1',
		'port': 8888,
		'socket_path': '',
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Loop = app.Loop
		self.Writers = set()

		self.Host = self.Config['host']
		self.Port = int(self.Config['port']) if self.Config['port'] else None
		self.SocketPath = self.Config['socket_path'] or None

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
		if self.SocketPath:
			server = await asyncio.start_unix_server(
				self._handler_wrapper,
				path=self.SocketPath,
				loop=self.Loop
			)
		else:
			server = await asyncio.start_server(
				self._handler_wrapper,
				self.Config['host'], int(self.Config['port']),
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
