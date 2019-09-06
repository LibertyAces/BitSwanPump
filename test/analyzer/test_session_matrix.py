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


	def test_matrix_store_event(self):
		dtype = [
			('f1', 'U20'),
			('f2', 'i8'),
			('f3', 'f8'),
			('f4', 'U30')
		]
		matrix = bspump.analyzer.SessionMatrix(app=self.App, dtype=dtype)
		index = matrix.add_row("abc")
		event = {
			'id': 'abc',
			'f0' : 7,
			'f1': 'abcd',
			'f2': 123,
			'f3' : 123.0
		}
		matrix.store_event(index, event)
		row = np.zeros(1, dtype=dtype)
		row['f1'] = event['f1']
		row['f2'] = event['f2']
		row['f3'] = event['f3']
		row['f4'] = ''

		for key in row.dtype.names:
			self.assertEqual(row[key], matrix.Array[index][key])

		index = matrix.add_row("bcd")
		event = {
			'id' : 'bcd',
			'f0' : 666,
			'f2': 88,
			'f4': 'cdef'
		}
		
		matrix.store_event(index, event, keys=['f2', 'f4', 'f5'])
		row = np.zeros(1, dtype=dtype)
		row['f1'] = ''
		row['f2'] = event['f2']
		row['f3'] = 0
		row['f4'] = event['f4']
		
		for key in row.dtype.names:
			self.assertEqual(row[key], matrix.Array[index][key])
		

	def test_matrix_decode_row(self):
		dtype = [
			('f0', 'U3'),
			('f1', 'U8'),
		]
		matrix = bspump.analyzer.SessionMatrix(app=self.App, dtype=dtype, config={'primary_name':'event_id'})
		event_id = 'abc'
		index = matrix.add_row(event_id)
		matrix.Array[index]['f0'] = 'aaa'
		matrix.Array[index]['f1'] = 'bbb'

		event = matrix.decode_row(index)
		self.assertEqual(len(event), 3)
		self.assertEqual(event['event_id'], event_id)
		self.assertEqual(event['f0'], matrix.Array[index]['f0'])
		self.assertEqual(event['f1'], matrix.Array[index]['f1'])

		event_id = 'bcd'
		index = matrix.add_row(event_id)
		matrix.Array[index]['f0'] = 'bbb'
		matrix.Array[index]['f1'] = 'ccc'

		event = matrix.decode_row(index, keys=['f0'])
		self.assertEqual(len(event), 2)
		self.assertEqual(event['event_id'], event_id)
		self.assertEqual(event['f0'], matrix.Array[index]['f0'])



