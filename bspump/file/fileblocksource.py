import logging
from .fileabcsource import FileABCSource

#

L = logging.getLogger(__file__)

#

class FileBlockSource(FileABCSource):

	async def read(self, filename, f):
		await self.Pipeline.ready()
		event = f.read()
		self.process(event)
