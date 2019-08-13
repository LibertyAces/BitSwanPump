import logging
import time

import numpy as np
from ..matrix.matrix import Matrix

##

L = logging.getLogger(__name__)

##

class GeoMatrix(Matrix):
	'''
		Matrix, specific for `GeoAnalyzer`.
		`bbox` is the dictionary with `max_lat`, `min_lat`, `max_lon` and `min_lon` 
		for corner gps-coordinates.
		`GeoMatrix` is 2d projection of real-world coordinates on a plane with pointers
		to `IdsToMembers`, where objects can be kept. 

	'''

	ConfigDefaults = {
		"max_lat": 71.26,  # Europe endpoints
		"min_lat": 23.33,
		"min_lon": -10.10,
		"max_lon": 40.6,
	}

	def __init__(self, app, dtype:list, bbox=None, resolution=5, id=None, config=None):
		if bbox is None:
			bbox = {
				"min_lat": float(self.ConfigDefaults["min_lat"]),
				"max_lat": float(self.ConfigDefaults["max_lat"]),
				"min_lon": float(self.ConfigDefaults["min_lon"]),
				"max_lon": float(self.ConfigDefaults["max_lon"]),
			}
		
		self.Bbox = bbox
		self.Resolution = resolution
		self.update_matrix_dimensions()
		dtype = dtype[:]
		dtype.extend([
			('ids', "({},1)i4".format(self.MapWidth))
		])
		super().__init__(app, dtype=dtype, id=id, config=config)
		
		self.MembersToIds = {}
		self.IdsToMembers = {}
		self.Array = np.zeros(self.MapHeight, dtype=self.DType)
		self.Array["ids"][:, :, :] = -1

	
	def is_in_boundaries(self, lat, lon):
		'''
		Check, if coordinates are within the bbox coordinates.
		'''
		if (lat >= self.Bbox["max_lat"]) or (lat <= self.Bbox["min_lat"]):
			return False

		if (lon >= self.Bbox["max_lon"]) or (lat <= self.Bbox["min_lon"]):
			return False

		return True


	def update_matrix_dimensions(self):
		'''
			Calculation of MapHeight and MapWidth.
		'''
		self.SizeWidth = self.get_gps_distance(self.Bbox["min_lat"], self.Bbox["min_lon"], self.Bbox["min_lat"], self.Bbox["max_lon"])
		self.SizeHeight = self.get_gps_distance(self.Bbox["min_lat"], self.Bbox["min_lon"], self.Bbox["max_lat"], self.Bbox["min_lon"])
		self.MapHeight = int(np.ceil(self.SizeHeight / self.Resolution))
		self.MapWidth = int(np.ceil(self.SizeWidth / self.Resolution))
		
		# Correction
		self.SizeWidth = int(self.MapWidth * self.Resolution)
		self.SizeHeight = int(self.MapHeight * self.Resolution)


	def degrees_to_radians(self, degrees):
		return degrees * np.pi / 180


	def get_gps_distance(self, lat1, lon1, lat2, lon2):
		'''
			Calculation of distance between 2 gps-coordinates in km.
		'''
		R = 6371
		dLat = self.degrees_to_radians(lat2-lat1)
		dLon = self.degrees_to_radians(lon2-lon1)
		lat1 = self.degrees_to_radians(lat1)
		lat2 = self.degrees_to_radians(lat2)
		a = np.sin(dLat/2) * np.sin(dLat/2) + np.sin(dLon/2) * np.sin(dLon/2) * np.cos(lat1) * np.cos(lat2)
		c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
		return R * c


	def project_equirectangular(self, lat, lon):
		'''
			Converts latitude and longitude into row and column indexes.
		'''
		column = ((lon - self.Bbox['min_lon']) * ((self.MapWidth - 1) / (self.Bbox['max_lon'] - self.Bbox['min_lon'])))
		row = (((lat * (-1)) + self.Bbox['max_lat']) * ((self.MapHeight - 1) / (self.Bbox['max_lat'] - self.Bbox['min_lat'])))
		return int(row), int(column)


	def inverse_equirectangular(self, row, column):
		'''
			Converts row and column into latitude and longitude.
		'''
		row += 0.5
		column += 0.5
		
		lat = -((row / (self.MapHeight - 1) * (self.Bbox['max_lat'] - self.Bbox['min_lat'])) - self.Bbox['max_lat'])
		lon = column * (self.Bbox['max_lon'] - self.Bbox['min_lon']) / (self.MapWidth - 1) + self.Bbox['min_lon']

		return lat, lon


	def remove_record(self, storage_id, label):
		'''
			Remove a record from storage.
		'''
		storage_member = self.IdsToMembers.get('id')
		if storage_member is not None:
			self.IdsToMembers['id'].pop(label)
