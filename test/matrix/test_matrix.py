import unittest
import time

import bspump
import bspump.matrix
import bspump.unittest


class TestMatrix(bspump.unittest.TestCase):
	def test_matrix(self):
		matrix = bspump.Matrix(
			app = self.App,
			dtype = [
				('f1', 'i8'),
				('f2', 'i8'),
				('f3', 'i8'),
			]
		)

		for i in range(100):
			n = matrix.add_row()
			matrix.Array[n][0] = 1 # Access by a field index
			matrix.Array[n]['f2'] = 1 # Access by a field name
			matrix.Array[n][2] = 1
			self.assertEqual(n, i)

		closed = set()
		closed |= matrix.ClosedRows

		for i in range(20, 40):
			matrix.close_row(i)
			closed.add(i)
			self.assertIn(i, matrix.ClosedRows)

		self.assertEqual(closed, matrix.ClosedRows)

		for i in range(20):
			n = matrix.add_row()
			self.assertIn(n, closed)


	def test_matrix_zeros(self):
		matrix = bspump.Matrix(app=self.App)

		for i in range(100):
			n = matrix.add_row()
			self.assertEqual(n, i)

		matrix.zeros()

		self.assertEqual(matrix.Array.shape, (0,))


	def test_matrix_flush(self):
		matrix = bspump.Matrix(app=self.App)

		for i in range(100):
			n = matrix.add_row()
			self.assertEqual(n, i)

		for i in range(20, 40):
			matrix.close_row(i)
			self.assertIn(i, matrix.ClosedRows)

		matrix.flush()

		self.assertEqual(len(matrix.ClosedRows), 0)


	def test_matrix_dtypes(self):
		matrix = bspump.Matrix(
			app = self.App,
			dtype = [
				('f1', 'U20'),
				('f2', 'i8'),
				('f3', 'i8'),
			]
		)

		row_index = matrix.add_row()
		row = matrix.Array[row_index]
		
		row['f1'] = "Ahoj"
		row['f2'] = 64
