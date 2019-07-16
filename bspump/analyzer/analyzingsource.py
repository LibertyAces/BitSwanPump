import logging
import asyncio
import asab
from ..abc.source import TriggerSource

#

L = logging.getLogger(__name__)

#

class AnalyzingSource(TriggerSource):
	

	def __init__(self, app, pipeline, matrix_id, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		svc = app.get_service("bspump.PumpService")
		self.AnalyzeMatrix = svc.locate_matrix(matrix_id)


	
	async def cycle(self):
		print("cycle!")
		try:
			event = await self.AnalyzeMatrix.analyze()
			await self.process(event)
		except BaseException as e:
			L.exception("Error while analyzing the matrix")


