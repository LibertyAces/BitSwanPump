import logging
import time
import asab

import numpy as np

from .analyzer import Analyzer
from .geomatrix import GeoMatrix 


##

L = logging.getLogger(__name__)

##

class GeoAnalyzer(Analyzer):
		'''
		This is the analyzer for events with geografical points dimension.

		`GeoAnalyzer` operates over the `GeoMatrix` object.
		`matrix_id` is an id of `GeoMatrix` object defined alternatively.

	'''
	ConfigDefaults = {
		"resolution": 5,  # 5 km in one cell
		"max_lat": 71.26,  # Europe endpoints
		"min_lat": 23.33,
		"min_lon": -10.10,
		"max_lon": 40.6,
	}

	def __init__(self, app, pipeline, matrix_id=None, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		svc = app.get_service("bspump.PumpService")
		if matrix_id is None:
			bbox = {
				"min_lat": float(self.ConfigDefaults["min_lat"]),
				"max_lat": float(self.ConfigDefaults["max_lat"]),
				"min_lon": float(self.ConfigDefaults["min_lon"]),
				"max_lon": float(self.ConfigDefaults["max_lon"]),
			}
			self.GeoMatrix = GeoMatrix(app, bbox, resolution=5)
			svc.add_matrix(self.GeoMatrix)
		else:
			self.GeoMatrix = svc.locate_matrix(matrix_id)
		
		self.Matrix = self.GeoMatrix.Matrix['geo_matrix']  # alias
