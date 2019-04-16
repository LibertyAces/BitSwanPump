import logging
import time
import asab

import numpy as np

from .analyzer import Analyzer
from .geomatrixcontainer import GeoMatrixContainer 


##

L = logging.getLogger(__name__)

##

class GeoAnalyzer(Analyzer):
	
	ConfigDefaults = {
		"resolution": 5,  # 5 km in one cell
		"max_lat": 71.26,  # Europe endpoints
		"min_lat": 23.33,
		"min_lon": -10.10,
		"max_lon": 40.6,
		"analyze_period": 60*60, # for now
	}

	def __init__(self, app, pipeline, container=None, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		
		if container is None:
			bbox = {
				"min_lat": float(self.ConfigDefaults["min_lat"]),
				"max_lat": float(self.ConfigDefaults["max_lat"]),
				"min_lon": float(self.ConfigDefaults["min_lon"]),
				"max_lon": float(self.ConfigDefaults["max_lon"]),
			}
			self.GeoMatrixContainer = GeoMatrixContainer(app, pipeline, bbox, resolution=5)
		else:
			self.GeoMatrixContainer = container
		
		self.Matrix = self.GeoMatrixContainer.Matrix['geo_matrix']  # alias
		self.AnalyzePeriod = int(self.Config['analyze_period'])
		self.AnalyzeTimer = asab.Timer(app, self._on_tick_analyze, autorestart=True)
		self.AnalyzeTimer.start(self.AnalyzePeriod)


	async def _on_tick_analyze(self):
		await self.analyze()