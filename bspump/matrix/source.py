import logging

from ..abc.source import TriggerSource

#

L = logging.getLogger(__name__)

#


class MatrixSource(TriggerSource):


	def __init__(self, app, pipeline, matrix_id, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		svc = app.get_service("bspump.PumpService")
		self.AnalyzeMatrix = svc.locate_matrix(matrix_id)


	async def cycle(self):
		await self.process(self.AnalyzeMatrix)
