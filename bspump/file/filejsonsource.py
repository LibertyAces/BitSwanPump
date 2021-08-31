import logging
import json
from .fileabcsource import FileABCSource


L = logging.getLogger(__file__)


class FileJSONSource(FileABCSource):

	'''
	Description: This file source is optimized to load even large JSONs from a file and parse that.
	The loading & parsing is off-loaded to the worker thread so that it doesn't block the IO loop.

	'''

	def __init__(self, app, pipeline, id=None, config=None):
		'''
		Description:

		**Parameters**

		app :

		pipeline :

		id : ID, default= None
			ID

		config : JSON, default = None
			configuration file with additional information

		'''
		super().__init__(app, pipeline, id=id, config=config)
		self.ProactorService = app.get_service("asab.ProactorService")


	async def read(self, filename, f):
		"""
		Description:

		**Parameters**

		filename :

		f :

		"""
		await self.Pipeline.ready()

		worker = self.ProactorService.execute(json.load, f)
		await worker
		event = worker.result()
		await self.process(event, {
			"filename": filename
		})
