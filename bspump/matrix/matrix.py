import abc
import collections
import logging
import os
import numpy as np

import asab
from .index import Index, PersistentIndex
from .closedrows import ClosedRows, PersistentClosedRows

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
		'path': '',
		'max_closed_rows_capacity': 0.2,
	}

	def __init__(self, app, dtype='float_', persistent=False, id=None, config=None):
		if not isinstance(dtype, str):
			dtype = dtype[:]
		
		self.Id = id if id is not None else self.__class__.__name__
		super().__init__("matrix:{}".format(self.Id), config=config)

		self.App = app
		self.Loop = app.Loop
		self.Path = self.Config['path']
		if persistent:
			if not os.path.exists(self.Path):
				os.makedirs(self.Path)
		
			self.ArrayPath = os.path.join(self.Path, 'array.dat')
		else:
			self.ArrayPath = None
		
		self.DType = dtype
		self.Persistent = persistent
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
		if self.Persistent:
			path = os.path.join(self.Path, 'closed_rows.dat')
			if os.path.exists(self.ArrayPath):
				self.Array = np.memmap(self.ArrayPath, dtype=self.DType, mode='readwrite')
				self.Array = self.Array.reshape(self.reshape(self.Array.shape))
				array = np.memmap(self.ArrayPath,  dtype=self.DType, mode='w+', shape=self.Array.shape)
				array[:] = self.Array[:]
				self.Array = array
			else:
				array = np.zeros(self.build_shape(rows), dtype=self.DType)
				self.Array = np.memmap(self.ArrayPath,  dtype=self.DType, mode='w+', shape=array.shape)

			self.ClosedRows = PersistentClosedRows(path, size=self.Array.shape[0])
		else:
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
		if self.Persistent:
			array = np.memmap(self.ArrayPath, dtype=self.DType, mode='w+', shape=self.Array.shape)
			array[:] = self.Array[:]
			self.Array = array

		self.ClosedRows.reset(self.Array.shape[0])
		self.Gauge.set("rows.closed", 0)
		self.Gauge.set("rows.active", self.Array.shape[0])
		return closed_indexes, saved_indexes


	def close_row(self, row_index, clear=True):
		assert(row_index < self.Array.shape[0])
		if row_index in self.ClosedRows:
			return False

		if clear:
			self.Array[row_index] = np.zeros(1, dtype=self.DType)
		
		self.ClosedRows.add(row_index)

		crc = len(self.ClosedRows)
		self.Gauge.set("rows.active", self.Array.shape[0] - crc)
		self.Gauge.set("rows.closed", crc)
		return True


	def close_rows(self, indexes, clear=True):
		for index in indexes:
			self.close_row(index, clear=clear)

		if len(self.ClosedRows) >= self.MaxClosedRowsCapacity * self.Array.shape[0]:
			self.flush()


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
		if self.Persistent:		
			self.persistent_resize(current_rows, rows)
		else:
			self.Array.resize((current_rows + rows,) + self.Array.shape[1:], refcheck=False)

		self.ClosedRows.extend(current_rows, self.Array.shape[0])


	def persistent_resize(self, current_rows, rows):
		array = np.zeros(self.Array.shape, dtype=self.DType)
		array[:] = self.Array[:]
		array.resize((current_rows + rows,) + self.Array.shape[1:], refcheck=False)
		self.Array = np.memmap(self.ArrayPath,  dtype=self.DType, mode='w+', shape=array.shape)
		self.Array[:] = array[:]


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


class NamedMatrix(Matrix):

	def __init__(self, app, dtype='float_', persistent=False, id=None, config=None):
		super().__init__(app, dtype=dtype, persistent=persistent, id=id, config=config)
		self.PubSub = asab.PubSub(app)


	def zeros(self):
		super().zeros()
		if self.Persistent:
			path  = os.path.join(self.Path, 'map.dat')
			self.Index = PersistentIndex(path, self.Array.shape[0])
		else:
			self.Index = Index()


	def _grow_rows(self, rows=1):
		super()._grow_rows(rows)
		self.Index.extend(self.Array.shape[0])


	def flush(self):
		'''
		The matrix will be recreated without rows from `ClosedRows`.
		'''
		closed_indexes, saved_indexes = super().flush()
		self.Index.clean(closed_indexes)
		return closed_indexes, saved_indexes


	def add_row(self, row_name: str):
		assert(row_name is not None)

		row_index = super().add_row()
		self.Index.add_row(row_name, row_index)
		self.PubSub.publish("Matrix changed!")
		return row_index


	def close_row(self, row_index, clear=True):
		closed = super().close_row(row_index, clear=clear)
		if closed:
			self.Index.pop_index(row_index)
			self.PubSub.publish("Matrix changed!")
			return True
		
		return False


	def get_row_index(self, row_name: str):
		return self.Index.get_row_index(row_name)


	def get_row_name(self, row_index: int):
		return self.Index.get_row_name(row_index)


	def serialize(self):
		if self.Persistent:
			raise RuntimeError("Not Implemented")
		
		serialized = {}
		serialized['Index'] = self.Index.serialize()
		serialized['ClosedRows'] =self.ClosedRows.serialize()
		serialized['DType'] = self.DType
		serialized['Array'] = self.Array.tolist()
		return serialized


	def deserialize(self, data):
		if self.Persistent:
			raise RuntimeError("Not Implemented")

		self.Index.deserialize(data['Index'])
		self.ClosedRows.deserialize(data['ClosedRows'])

		if isinstance(data['DType'], str):
			self.DType = data['DType']
		else:
			self.DType = []
			for member in data['DType']:
				self.DType.append(tuple(member))

		array = []
		for member in data['Array']:
			array.append(tuple(member))

		self.Array = np.array(array, dtype=self.DType)
