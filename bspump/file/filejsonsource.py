import logging
import json
from .fileabcsource import FileABCSource


L = logging.getLogger(__file__)


class FileJSONSource(FileABCSource):

	'''
	This file source is optimized to load even large JSONs from a file and parse that.
	The loading & parsing is off-loaded to the worker thread so that it doesn't block the IO loop.
	'''

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.ProactorService = app.get_service("asab.ProactorService")


	async def read(self, filename, f):
		await self.Pipeline.ready()

		worker = self.ProactorService.execute(json.load, f)
		await worker
		event = worker.result()
		await self.process(event, {
			"filename": filename
		})
