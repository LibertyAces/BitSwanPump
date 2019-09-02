import unittest
import time
import numpy as np

import bspump
import bspump.analyzer
import bspump.unittest


class TestGeoMatrix(bspump.unittest.TestCase):

	def test_matrix(self):
		bbox = {"min_lon": 14.259097, "max_lon": 14.589601, "min_lat": 49.974702, "max_lat": 50.160150} 
		matrix = bspump.analyzer.GeoMatrix(app=self.App, bbox=bbox, resolution=5)
		self.assertEqual(int(matrix.MapHeight * matrix.Resolution), int(matrix.SizeHeight))
		self.assertEqual(int(matrix.MapWidth * matrix.Resolution), int(matrix.SizeWidth))
		self.assertEqual(matrix.Array.shape, (matrix.MapHeight, matrix.MapWidth))


	def test_matrix_is_in_boundaries(self):
		bbox = {"min_lon": 14.259097, "max_lon": 14.589601, "min_lat": 49.974702, "max_lat": 50.160150} 
		matrix = bspump.analyzer.GeoMatrix(app=self.App, bbox=bbox, resolution=5)
		coordinates = [(0, 0), (0, 50), (14.3, 51), (14.3, 50), (13, 50)]
		ground_truths = [False, False, False, True, False]

		for i in range(len(coordinates)):
			lat = coordinates[i][1]
			lon = coordinates[i][0]
			ground_truth = ground_truths[i]
			matrix_answer = matrix.is_in_boundaries(lat, lon)
			self.assertIs(matrix_answer, ground_truth)
			


	def test_matrix_equirectangular(self):
		bbox = {"min_lon": 14.259097, "max_lon": 14.589601, "min_lat": 49.974702, "max_lat": 50.160150} 
		matrix = bspump.analyzer.GeoMatrix(app=self.App, bbox=bbox, resolution=5)

		indexes = [(0, 0), (0, np.ceil(matrix.MapWidth / 2)), (0, matrix.MapWidth - 1), ((np.ceil(matrix.MapHeight / 2)), 0), (matrix.MapHeight - 1, matrix.MapWidth - 1)]

		for i in range(len(indexes)):
			row = indexes[i][0]
			column = indexes[i][1]
			lat, lon  = matrix.inverse_equirectangular(row, column)
			row_, column_ =  matrix.project_equirectangular(lat, lon)
			self.assertEqual(row_, row)
			self.assertEqual(column_, column)
