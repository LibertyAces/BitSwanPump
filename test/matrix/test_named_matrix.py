import unittest
import collections
import time

import bspump
import bspump.matrix
import bspump.unittest


class TestNamedMatrix(bspump.unittest.TestCase):

	def test_matrix_zeros(self):
		matrix = bspump.matrix.NamedMatrix(
			app = self.App,
			dtype = "int_")

		matrix.zeros()
		self.assertEqual(matrix.Array.shape, (0,))
		self.assertEqual(len(matrix.N2IMap), 0)
		self.assertEqual(len(matrix.I2NMap), 0)


	def test_matrix_flush(self):
		matrix = bspump.matrix.NamedMatrix(app=self.App)
		n = 100
		indexes = []
		for i in range(n):
			index = matrix.add_row(str(i))
			indexes.append(index)
			matrix.Array[index] = i
		
		check_array = matrix.Array[40:100]

		for i in range(0, 40):
			matrix.close_row(i)

		matrix.flush()
		self.assertEqual(matrix.Array.shape, (n - 40,))
		self.assertEqual(len(matrix.N2IMap), n - 40)
		self.assertEqual(len(matrix.I2NMap), n - 40)
		self.assertEqual(len(check_array), len(matrix.Array))
		for i in range(len(check_array)):
			self.assertEqual(check_array[i], matrix.Array[i])


	def test_matrix_add_row(self):
		matrix = bspump.matrix.NamedMatrix(app=self.App)
		n = 100
		n2i = collections.OrderedDict()
		i2n = collections.OrderedDict()
		for i in range(n):
			name = "id_" + str(i)
			index = matrix.add_row(name)
			n2i[name] = index
			i2n[index] = name

		self.assertEqual(n2i, matrix.N2IMap)
		self.assertEqual(i2n, matrix.I2NMap)


	def test_matrix_close_row(self):
		matrix = bspump.matrix.NamedMatrix(app=self.App)
		n = 100
		for i in range(n):
			index = matrix.add_row(str(i))

		for i in range(0, 5):
			matrix.close_row(i)
			self.assertNotIn(i, matrix.I2NMap)

		self.assertEqual(len(matrix.I2NMap), len(matrix.N2IMap))


	def test_matrix_get_row_index(self):
		matrix = bspump.matrix.NamedMatrix(app=self.App)
		n = 100
		for i in range(n):
			name = "id_" + str(i)
			index = matrix.add_row(name)
			index_obtained = matrix.get_row_index(name)
			self.assertEqual(i, index_obtained)
		

	def test_matrix_get_row_name(self):
		matrix = bspump.matrix.NamedMatrix(app=self.App)
		n = 100
		for i in range(n):
			name = "id_" + str(i)
			index = matrix.add_row(name)
			name_obtained = matrix.get_row_name(i)
			self.assertEqual(name, name_obtained)
