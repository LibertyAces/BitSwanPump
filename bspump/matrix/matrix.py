import abc
import collections
import logging
import os
import numpy as np

import asab
from .utils.closedrows import ClosedRows, PersistentClosedRows

###

L = logging.getLogger(__name__)

###


class Matrix(abc.ABC, asab.ConfigObject):
	'''
		Generic `Matrix` object.

		Matrix structure is organized in a following hiearchical order:

		Matrix -> Rows -> Columns -> Cells

		Cells have unified data format across the whole matrix.
		This format is specified by a `dtype`.
		It can be a simple integer or float but also a complex dictionary type with names and types of the fields.

		The description of types that can be used for a `dtype` of a cell:

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

		For more details, see https://docs.scipy.org/doc/numpy/reference/arrays.dtypes.html


		Object main attributes:
		`Array` is numpy ndarray, the actual data representation of the matrix object.
		`ClosedRows` is a set, where some row ids can be stored before deletion during the matrix rebuild.

	'''

	ConfigDefaults = {
		'max_closed_rows_capacity': 0.2,
	}

	def __init__(self, app, dtype='float_', persistent=False, id=None, config=None):
		if not isinstance(dtype, str):
			dtype = dtype[:]
		
		self.Id = id if id is not None else self.__class__.__name__
		super().__init__("matrix:{}".format(self.Id), config=config)

		self.App = app
		self.Loop = app.Loop
		
		self.DType = dtype
		self.MaxClosedRowsCapacity = float(self.Config['max_closed_rows_capacity'])
		self.zeros()
		
		metrics_service = app.get_service('asab.MetricsService')
		self.Gauge = metrics_service.create_gauge(
			"RowCounter",
			tags={
				'matrix': self.Id,
			},
			init_values={
				"rows.closed": 0,
				"rows.active": 0,
			}
		)


	def zeros(self, rows=1):
		self.Array = np.zeros(self.build_shape(rows), dtype=self.DType)
		self.ClosedRows = ClosedRows()
		self.ClosedRows.add(0)


	def flush(self):
		'''
		The matrix will be recreated without rows from `ClosedRows`.
		'''
		indexes = set(range(self.Array.shape[0]))
		closed_indexes = set()
		closed_indexes |= self.ClosedRows.get_rows()
		saved_indexes = list(indexes - closed_indexes)
		saved_indexes.sort()
		self.Array = self.Array.take(saved_indexes, axis=0)
		self.ClosedRows.flush(self.Array.shape[0])
		self.Gauge.set("rows.closed", 0)
		self.Gauge.set("rows.active", self.Array.shape[0])
		return closed_indexes, saved_indexes


	def close_rows(self, row_names, clear=True):
		pass


	def close_row(self, row_name, clear=True):
		pass


	def add_row(self):
		try:
			return self.ClosedRows.pop()
		except KeyError:
			self._grow_rows(max(5, int(0.10 * self.Array.shape[0])))
			return self.ClosedRows.pop()
		finally:
			crc = len(self.ClosedRows)
			self.Gauge.set("rows.active", self.Array.shape[0] - crc)
			self.Gauge.set("rows.closed", crc)


	def build_shape(self, rows=0):
		'''
		Override this method to have a control over the shape of the matrix.
		'''
		return rows,


	def reshape(self, shape):
		return shape


	def _grow_rows(self, rows=1):
		'''
		Override this method to gain control on how a new closed rows are added to the matrix
		'''
		current_rows = self.Array.shape[0]	
		self.Array.resize((current_rows + rows,) + self.Array.shape[1:], refcheck=False) # TODO
		self.ClosedRows.extend(current_rows, self.Array.shape[0])


	def time(self):
		return self.App.time()


	async def analyze(self):
		'''
			The `Matrix` itself can run the `analyze()`.
			It is not recommended to iterate through the matrix row by row (or cell by cell).
			Instead use numpy fuctions. Examples:
			1. You have a vector with n rows. You need only those row indeces, where the cell content is more than 10.
			Use `np.where(vector > 10)`.
			2. You have a matrix with n rows and m columns. You need to find out which rows
			fully consist of zeros. use `np.where(np.all(matrix == 0, axis=1))` to get those row indexes.
			Instead `np.all()` you can use `np.any()` to get all row indexes, where there is at least one zero.
			3. Use `np.mean(matrix, axis=1)` to get means for all rows.
			4. Usefull numpy functions: `np.unique()`, `np.sum()`, `np.argmin()`, `np.argmax()`.
		'''
		pass



class PersistentMatrix(Matrix):
	ConfigDefaults = {
		'path': '',
	}

	def __init__(self, app, dtype='float_', id=None, config=None):
		# TODO super
		super().__init__(app, dtype=dtype, id=id, config=config)


	def create_path(self):
		self.Path = self.Config['path']
		if not os.path.exists(self.Path):
			os.makedirs(self.Path)

		self.ArrayPath = os.path.join(self.Path, 'array.dat')


	def zeros(self, rows=1):
		self.create_path()
		if os.path.exists(self.ArrayPath):
			self.Array = np.memmap(self.ArrayPath, dtype=self.DType, mode='readwrite')
			self.Array = self.Array.reshape(self.reshape(self.Array.shape))
		else:
			array = np.zeros(self.build_shape(rows), dtype=self.DType)
			self.Array = np.memmap(self.ArrayPath,  dtype=self.DType, mode='w+', shape=array.shape)

		path = os.path.join(self.Path, 'closed_rows.dat')
		self.ClosedRows = PersistentClosedRows(path, size=self.Array.shape[0])


	def flush(self):
		'''
		The matrix will be recreated without rows from `ClosedRows`.
		'''
		indexes = set(range(self.Array.shape[0]))
		closed_indexes = set()
		closed_indexes |= self.ClosedRows.get_rows()
		saved_indexes = list(indexes - closed_indexes)
		saved_indexes.sort()
		self.Array = self.Array.take(saved_indexes, axis=0)
		array = np.memmap(self.ArrayPath, dtype=self.DType, mode='w+', shape=self.Array.shape)
		array[:] = self.Array[:]
		self.Array = array

		self.ClosedRows.flush(self.Array.shape[0])
		self.Gauge.set("rows.closed", 0)
		self.Gauge.set("rows.active", self.Array.shape[0])
		return closed_indexes, saved_indexes


	def close_row(self, row_name, clear=True):
		row_index = self.Index.get_row_index(row_name)
		if (row_index in self.ClosedRows) or (row_index is None):
			return False

		if clear:
			self.Array[row_index] = np.zeros(1, dtype=self.DType)

		self.ClosedRows.add(row_index)

		if len(self.ClosedRows) >= self.MaxClosedRowsCapacity * self.Array.shape[0]:
			self.flush()

		crc = len(self.ClosedRows)
		self.Gauge.set("rows.active", self.Array.shape[0] - crc)
		self.Gauge.set("rows.closed", crc)
		return True


	def _grow_rows(self, rows=1):
		'''
		Override this method to gain control on how a new closed rows are added to the matrix
		'''
		current_rows = self.Array.shape[0]
		array = np.zeros(self.Array.shape, dtype=self.DType)
		array[:] = self.Array[:]
		array.resize((current_rows + rows,) + self.Array.shape[1:], refcheck=False)
		self.Array = np.memmap(self.ArrayPath, dtype=self.DType, mode='w+', shape=array.shape)
		self.Array[:] = array[:]
		self.ClosedRows.extend(current_rows, self.Array.shape[0])
