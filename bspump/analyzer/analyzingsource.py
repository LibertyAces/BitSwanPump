import logging
import asyncio
import asab
from ..common.routing import InternalSource

#

L = logging.getLogger(__name__)

#

class AnalyzingSource(InternalSource):
	
	ConfigDefaults = {
		"analyze_period": 60,
	}

	def __init__(self, app, pipeline, matrix_id, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		svc = app.get_service("bspump.PumpService")
		self.AnalyzeMatrix = svc.locate_matrix(matrix_id)
		self.AnalyzePeriod = int(self.Config['analyze_period'])

		self.Timer = asab.Timer(app, self.on_clock_tick, autorestart=True)
		self.Timer.start(self.AnalyzePeriod)


	
	async def on_clock_tick(self):
		if not self.BackPressure:
			await self.AnalyzeMatrix.analyze()


