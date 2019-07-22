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

		self.zeros()


	def zeros(self, shape=0):
		self.ClosedRows = set()
		self.Matrix = np.zeros(shape, dtype=self.DType)


	def flush(self):
		'''
		The matrix will be recreated without rows from `ClosedRows`.
		'''
	
		saved_indexes = []
		for row_index in range(self.Matrix.shape[0]):
			if row_index not in self.ClosedRows:
				saved_indexes.append(row_index)

		self.Matrix = self.Matrix[saved_indexes]
		self.ClosedRows = set()


	def close_row(self, row_index):
		assert(row_index < self.Matrix.shape[0])
		self.ClosedRows.add(row_index)


	def add_row(self):
		try:
			return self.ClosedRows.pop()
		except KeyError:
			self._grow_rows(max(5, int(1.10 * self.Matrix.shape[0])))
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


	def zeros(self):
		super().zeros()
		self.RowN2IMap = collections.OrderedDict()
		self.RowI2NMap = collections.OrderedDict()


	def flush(self):
		'''
		The matrix will be recreated without rows from `ClosedRows`.
		'''
	
		n2imap = collections.OrderedDict()
		i2nmap = collections.OrderedDict()
		saved_indexes = []

		i = 0
		for row_name, row_index in self.RowN2IMap.items():
			if row_index not in self.ClosedRows:
				n2imap[row_name] = i
				i2nmap[i] = row_name
				saved_indexes.append(row_index)
				i += 1

		self.Matrix = self.Matrix[saved_indexes]
		self.RowN2IMap = n2imap
		self.RowI2NMap = i2nmap
		self.ClosedRows = set()


	def add_row(self, row_name):
		row_id = super().add_row()

		self.RowN2IMap[row_name] = row_id
		self.RowI2NMap[row_id] = row_name

		return row_id


	def close_row(self, row_index):
		super().close_row(row_index)

		row_name = self.RowI2NMap.pop(row_index)
		del self.RowN2IMap[row_name]


	def get_row_index(self, row_name):
		return self.RowN2IMap.get(row_name)


	def get_row_name(self, row_index):
		return self.RowI2NMap.get(row_index)
