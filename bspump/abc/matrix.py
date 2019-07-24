import abc
import time
import logging
import collections

import numpy as np

import asab


###

L = logging.getLogger(__name__)

###


class MatrixABC(abc.ABC, asab.ConfigObject):
	'''
		General `Matrix` object.

		`column_names` is an array with names of each column, with the same length as `column_formats`.

		`column_formats` is an array, each element contains the letter from the table + number:

			+------------+------------------+
			| Name       | Definition       |
			+============+==================+
			| 'b'        | Byte             |
			+------------+------------------+
			| 'i'        | Signed integer   |
			+------------+------------------+
			| 'u'        | Unsigned integer |
			+------------+------------------+
			| 'f'        | Floating point   |
			+------------+------------------+
			| 'c'        | Complex floating |
			|            | point            |
			+------------+------------------+
			| 'S'        | String           |
			+------------+------------------+
			| 'U'        | Unicode string   |
			+------------+------------------+
			| 'V'        | Raw data         |
			+------------+------------------+

		Example: 'i8' stands for int64.
		It is possible to create a matrix with elements of specified format. The tuple with number of dimensions should 
		stand before the letter.
		Example: '(6, 3)i8' will create the matrix with n rows, 6 columns and 3 third dimensions with integer elements.
		
		
		Object main attributes:
		`Matrix` is numpy matrix, where number of rows is a number of unique ids and
		specified columns.
		`ClosedRows` is a set, where some row ids can be stored before deletion during the matrix rebuild.

	'''


	def __init__(self, app, column_names, column_formats, id=None, config=None):
		self.Id = id if id is not None else self.__class__.__name__
		super().__init__("matrix:{}".format(self.Id), config=config)

		self.App = app
		self.Loop = app.Loop

		self.DType = {
			'names':column_names,
			'formats':column_formats
		}

		# The dictionary that can be used to store an additional information for items in the matrix.
		# E.g. matrix contain the key to this dictionary (in a field of your choice).
		# WARNING: It is very rought concept and it is YOUR responsibility to manage data in the storage.
		# Specifically it means that YOU are responsible for removing obsolete items to prevent Storage bloating.
		self.Storage = {}

		self.zeros()


	def zeros(self, rows=0):
		self.ClosedRows = set()
		self.Matrix = np.zeros(rows, dtype=self.DType)


	def flush(self):
		'''
		The matrix will be recreated without rows from `ClosedRows`.
		'''
		indexes = set(range(self.Matrix.shape[0]))
		saved_indexes = list(indexes - self.ClosedRows)
		saved_indexes.sort()

		self.Matrix = self.Matrix[saved_indexes]
		self.ClosedRows = set()


	def close_row(self, row_index):
		assert(row_index < self.Matrix.shape[0])
		self.ClosedRows.add(row_index)


	def add_row(self):
		try:
			return self.ClosedRows.pop()
		except KeyError:
			self._grow_rows(max(5, int(0.10 * self.Matrix.shape[0])))
			return self.ClosedRows.pop()


	def _grow_rows(self, n=1):
		'''
		Override this method to gain control on how a new closed rows are added to the matrix
		'''
		i = self.Matrix.shape[0]
		rows = np.zeros(int(n), dtype=self.DType)
		self.Matrix = np.append(self.Matrix, rows)
		self.ClosedRows |= frozenset(range(i, i+n))


	def time(self):
		return self.App.time()


	async def analyze(self):
		pass



class NamedMatrixABC(MatrixABC):

	def __init__(self, app, column_names, column_formats, id=None, config=None):
		super().__init__(app, column_names, column_formats, id=id, config=config)
		metrics_service = app.get_service('asab.MetricsService')
		self.Gauge = metrics_service.create_gauge("RowCounter",
			tags = {
				'matrix': self.Id,
			},
			init_values = {
				"rows.all": 0,
				"rows.closed" : 0,
				"rows.active" : 0,
			}
		)


	def zeros(self):
		super().zeros()
		self.N2IMap = collections.OrderedDict()
		self.I2NMap = collections.OrderedDict()


	def flush(self):
		'''
		The matrix will be recreated without rows from `ClosedRows`.
		'''
	
		n2imap = collections.OrderedDict()
		i2nmap = collections.OrderedDict()
		saved_indexes = []

		i = 0
		for row_name, row_index in self.N2IMap.items():
			if row_index not in self.ClosedRows:
				n2imap[row_name] = i
				i2nmap[i] = row_name
				saved_indexes.append(row_index)
				i += 1

		self.Matrix = self.Matrix[saved_indexes]
		self.N2IMap = n2imap
		self.I2NMap = i2nmap
		self.ClosedRows = set()
		
		self.Gauge.set("rows.all", self.Matrix.shape[0])
		self.Gauge.set("rows.closed", 0)
		self.Gauge.set("rows.active", len(self.N2IMap))


	def add_row(self, row_name):
		row_index = super().add_row()
		assert(row_name is not None)
		self.N2IMap[row_name] = row_index
		self.I2NMap[row_index] = row_name

		self.Gauge.set("rows.all", self.Matrix.shape[0])
		self.Gauge.set("rows.closed", len(self.ClosedRows))
		self.Gauge.set("rows.active", len(self.N2IMap))

		return row_index


	def close_row(self, row_index):
		super().close_row(row_index)

		row_name = self.I2NMap.pop(row_index)
		del self.N2IMap[row_name]

		self.Gauge.set("rows.all", self.Matrix.shape[0])
		self.Gauge.set("rows.closed", len(self.ClosedRows))
		self.Gauge.set("rows.active", len(self.N2IMap))


	def get_row_index(self, row_name):
		return self.N2IMap.get(row_name)


	def get_row_name(self, row_index):
		return self.I2NMap.get(row_index)
