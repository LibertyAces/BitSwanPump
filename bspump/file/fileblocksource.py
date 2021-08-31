import logging
from .fileabcsource import FileABCSource


L = logging.getLogger(__file__)


class FileBlockSource(FileABCSource):
	"""
	Description:

	"""

	def __init__(self, app, pipeline, id=None, config=None):
		"""
		Description:

		**Parameters**

		app :

		pipeline :

		id : ID, default = None

		config : JSON, default = None

		"""
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
		# Load the file in a worker thread (to prevent blockage of the main loop)
		worker = self.ProactorService.execute(f.read)
		await worker
		event = worker.result()
		await self.process(event, {
			"filename": filename
		})
