import abc
import collections
import os
import logging

import numpy as np
import asab

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
		'path_prefix': 'examples/mmap/'
	}

	def __init__(self, app, dtype='float_', fetch=True, id=None, config=None):
		if not isinstance(dtype, str):
			dtype = dtype[:]
		self.Id = id if id is not None else self.__class__.__name__
		super().__init__("matrix:{}".format(self.Id), config=config)

		self.App = app
		self.Loop = app.Loop

		self.DType = dtype
		self.PathPrefix = self.Config['path_prefix']
		self.ArrayPath = os.path.join(self.PathPrefix, 'array.dat')
		self.ClosedRowsPath = os.path.join(self.PathPrefix, 'closed_rows.dat')
		self.ClosedRowsDType = 'i1'
		
		if not os.path.exists(self.PathPrefix):
			os.makedirs(self.PathPrefix)

		if fetch and os.path.exists(self.ArrayPath):
			self.prefetch()
		else:
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


	def prefetch(self):
		self.Array = np.memmap(self.ArrayPath, dtype=self.DType, mode='readwrite') #TODO
		self.ClosedRowsAlias = np.memmap(self.ClosedRowsPath, dtype=self.ClosedRowsDType, mode='readwrite')
		self.ClosedRows = set()
		for i in range(len(self.ClosedRowsAlias)):
			if self.ClosedRowsAlias[i] == 0:
				self.ClosedRows.add(i)


	def zeros(self, rows=0):
		self.ClosedRows = set([0])
		array = np.zeros(self.build_shape(1), dtype=self.DType)
		self.Array = np.memmap(self.ArrayPath,  dtype=self.DType, mode='w+', shape=array.shape)
		self.Array[:] = array[:]

		self.ClosedRowsAlias = np.memmap(self.ClosedRowsPath,  dtype=self.ClosedRowsDType, mode='w+', shape=(array.shape[0],))
		# TODO


	def flush(self):
		'''
		The matrix will be recreated without rows from `ClosedRows`.
		'''
		indexes = set(range(self.Array.shape[0]))
		saved_indexes = list(indexes - self.ClosedRows)
		saved_indexes.sort()

		self.Array = self.Array.take(saved_indexes)
		self.ClosedRows = set()
		self.ClosedRowsAlias = np.memmap(self.ClosedRowsPath,  dtype=self.ClosedRowsDType, mode='w+', shape=(self.Array.shape[0],)) #is it ones?
		self.ClosedRowsAlias[:] = 1
		
		self.Gauge.set("rows.closed", 0)
		self.Gauge.set("rows.active", self.Array.shape[0])


	def close_row(self, row_index, clear=True):
		assert(row_index < self.Array.shape[0])
		if row_index in self.ClosedRows:
			return

		if clear:
			self.Array[row_index] = np.zeros(1, dtype=self.DType)
		
		self.ClosedRows.add(row_index)
		self.ClosedRowsAlias[row_index] = 0
		crc = len(self.ClosedRows)
		self.Gauge.set("rows.active", self.Array.shape[0] - crc)
		self.Gauge.set("rows.closed", crc)


	def add_row(self):
		try:
			index = self.ClosedRows.pop()
			self.ClosedRowsAlias[index] = 1
			return index
		except KeyError:
			self._grow_rows(max(5, int(0.10 * self.Array.shape[0])))
			index = self.ClosedRows.pop()
			self.ClosedRowsAlias[index] = 1
			return index
		finally:
			crc = len(self.ClosedRows)
			self.Gauge.set("rows.active", self.Array.shape[0] - crc)
			self.Gauge.set("rows.closed", crc)
			


	def build_shape(self, rows=0):
		'''
		Override this method to have a control over the shape of the matrix.
		'''
		return rows,


	def _grow_rows(self, rows=1):
		'''
		Override this method to gain control on how a new closed rows are added to the matrix
		'''
		current_rows = self.Array.shape[0]
		array = np.zeros(self.Array.shape, dtype=self.DType)
		array[:] = self.Array[:]
		closed_rows = np.zeros(self.Array.shape[0], dtype=self.ClosedRowsDType)
		closed_rows[:] = self.ClosedRowsAlias[:]
		array.resize((current_rows + rows,) + self.Array.shape[1:], refcheck=False)
		closed_rows.resize((current_rows + rows,), refcheck=False)
		self.Array = np.memmap(self.ArrayPath,  dtype=self.DType, mode='w+', shape=array.shape)
		self.Array[:] = array[:]
		
		self.ClosedRows |= frozenset(range(current_rows, current_rows + rows))
		self.ClosedRowsAlias = np.memmap(self.ClosedRowsPath,  dtype=self.ClosedRowsDType, mode='w+', shape=closed_rows.shape) # TODO
		self.ClosedRowsAlias[:] = closed_rows[:]


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

	def __init__(self, app, dtype='float_', fetch=False, id=None, config=None):
		super().__init__(app, dtype=dtype, fetch=fetch, id=id, config=config)
		self.PubSub = asab.PubSub(app)
		self.MapPath = os.path.join(self.PathPrefix, 'map.dat')
		self.MapDType = 'U30'


	def zeros(self):
		super().zeros()
		self.N2IMap = collections.OrderedDict()
		self.I2NMap = collections.OrderedDict()

		self.MapAlias = np.memmap(self.PathPrefix + 'map.dat',  dtype='U30', mode='w+', shape=(self.Array.shape[0],)) # TODO


	def _grow_rows(self, rows=1):
		super()._grow_rows(rows)
		start = self.MapAlias.shape[0]
		end = self.Array.shape[0]

		map_alias = np.zeros(self.MapAlias.shape[0], dtype='U30')
		map_alias[:] = self.MapAlias[:]

		map_alias.resize(self.Array.shape[0], refcheck=False)
		self.MapAlias = np.memmap(self.PathPrefix + 'map.dat',  dtype='U30', mode='w+', shape=map_alias.shape)
		self.MapAlias[:] = map_alias[:]


	def prefetch(self):
		super().prefetch()
		self.N2IMap = collections.OrderedDict()
		self.I2NMap = collections.OrderedDict()
		self.MapAlias = np.memmap(self.PathPrefix + 'map.dat', dtype='U30', mode='readwrite')
		for i in range(len(self.MapAlias)):
			value = self.MapAlias[i]
			if value != '':
				self.I2NMap[i] = value
				self.N2IMap[value] = i


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

		self.Array = self.Array.take(saved_indexes)
		self.N2IMap = n2imap
		self.I2NMap = i2nmap
		self.ClosedRows = set()
		self.ClosedRowsAlias = np.memmap(self.PathPrefix + 'closed_rows.dat',  dtype=self.ClosedRowsDType, mode='w+', shape=(self.Array.shape[0],)) #TODO
		self.ClosedRowsAlias[:] = 1

		#TODO map!
		self.MapAlias = np.memmap(self.PathPrefix + 'map.dat',  dtype='U30', mode='w+', shape=(self.Array.shape[0],)) #TODO
		self.MapAlias[list(self.I2NMap.keys())] = np.array(list(self.I2NMap.values()), dtype='U30')
		self.Gauge.set("rows.closed", 0)
		self.Gauge.set("rows.active", self.Array.shape[0])
		self.PubSub.publish("Matrix changed!")


	def add_row(self, row_name: str):
		assert(row_name is not None)

		row_index = super().add_row()
		self.N2IMap[row_name] = row_index
		self.I2NMap[row_index] = row_name

		self.MapAlias[row_index] = row_name
		self.PubSub.publish("Matrix changed!")

		return row_index


	def close_row(self, row_index, clear=True):
		super().close_row(row_index, clear=clear)

		row_name = self.I2NMap.pop(row_index)
		del self.N2IMap[row_name]
		self.MapAlias[row_index] = ''
		self.PubSub.publish("Matrix changed!")


	def get_row_index(self, row_name: str):
		return self.N2IMap.get(row_name)


	def get_row_name(self, row_index: int):
		return self.I2NMap.get(row_index)


	def serialize(self):
		# TODO
		serialized = {}
		serialized['N2IMap'] = self.N2IMap
		serialized['I2NMap'] = self.I2NMap
		serialized['ClosedRows'] = list(self.ClosedRows)
		serialized['DType'] = self.DType
		serialized['Array'] = self.Array.tolist()
		return serialized


	def deserialize(self, data):
		# TODO
		self.N2IMap = data['N2IMap']
		self.I2NMap = data['I2NMap']
		self.ClosedRows = set(data['ClosedRows'])

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
