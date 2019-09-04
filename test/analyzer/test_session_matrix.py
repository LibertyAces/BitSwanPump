import unittest
import numpy as np

import bspump
import bspump.analyzer
import bspump.unittest



class TestSessionMatrix(bspump.unittest.TestCase):

	def test_matrix_store(self):
		dtype = [
			('f1', 'U20'),
			('f2', 'i8'),
		]
		matrix = bspump.analyzer.SessionMatrix(app=self.App, dtype=dtype)
		n = 100
		for i in range(n):
			name = "id_" + str(i)
			index = matrix.add_row(str(name))
			row = np.zeros(1, dtype=dtype)
			f1 = "something" + str(i)
			row['f1'] = f1
			row['f2'] = i
			matrix.store(name, row)
			self.assertEqual(matrix.Array[index]['f1'], f1)
			self.assertEqual(matrix.Array[index]['f2'], i)
