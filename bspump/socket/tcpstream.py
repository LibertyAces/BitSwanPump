import logging
import asyncio
from ..abc.source import Source

#

L = logging.getLogger(__name__)

#

class TCPStreamSource(Source):


	ConfigDefaults = {
		'host': '127.0.0.1',
		'port': 8888,
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Loop = app.Loop
		self.Writers = set()


	async def _handler(self, reader, writer):
		self.Writers.add(writer)

		try:
			while True:
				await self.Pipeline.ready()
				data = await reader.readline()
				# End of stream detected
				if len(data) == 0:
					writer.close()
					break
				await self.process(data)

		finally:
			self.Writers.remove(writer)


	async def main(self):
		# Start server
		server = await asyncio.start_server(
			self._handler,
			self.Config['host'], int(self.Config['port']),
			loop=self.Loop
		)

		await self.stopped()

		# Close server
		server.close()
		await server.wait_closed()

		# Close peer connections
		for writer in self.Writers:
			L.warning("Source '{}' closes connection to {}".format(
				self.Id,
				writer.transport.get_extra_info('peername'))
			)
			if writer.can_write_eof():
				writer.write_eof()
			writer.close()
