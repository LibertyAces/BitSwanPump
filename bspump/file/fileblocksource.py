import asyncio
import logging

from .fileabcsource import FileABCSource


L = logging.getLogger(__file__)


class FileBlockSource(FileABCSource):

	def __init__(self, app, pipeline, id=None, config=None):
		"""
		Description:

		**Parameters**

		app : Application
			Name of the Application.

		pipeline : Pipeline
			Name of the Pipeline.

		id : ID, default = None
			ID

		config : JSON, default = None
			Configuration file with additional information.
		"""
		super().__init__(app, pipeline, id=id, config=config)
		self.ProactorService = app.get_service("asab.ProactorService")


	async def read(self, filename, f):
		"""
		Loads a file.

		**Parameters**

		filename : file
			Name of the file.

		f :

		"""
		await self.Pipeline.ready()
		# Load the file in a worker thread (to prevent blockage of the main loop)
		worker = self.ProactorService.execute(f.read)
		
		try:
			await worker
		except asyncio.CancelledError:
			return
		
		event = worker.result()
		await self.process(event, {
			"filename": filename
		})
