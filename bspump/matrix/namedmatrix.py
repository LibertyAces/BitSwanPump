import logging
import os
import numpy as np

import asab
from .utils.index import Index, PersistentIndex
from .matrix import Matrix, PersistentMatrix

###

L = logging.getLogger(__name__)

###


class NamedMatrixMixin(Matrix):

	def _grow_rows(self, rows=1):
		super()._grow_rows(rows)
		self.Index.extend(self.Array.shape[0])


	def flush(self):
		'''
		The matrix will be recreated without rows from `ClosedRows`.
		'''
		closed_indexes, saved_indexes = super().flush()
		self.Index.flush(closed_indexes)
		return closed_indexes, saved_indexes


	def add_row(self, row_name: str):
		assert(row_name is not None)

		row_index = super().add_row()
		self.Index.add_row(row_name, row_index)
		self.PubSub.publish("Matrix changed!")
		return row_index


	def close_row(self, row_name, clear=True):
		row_index = self.Index.get_row_index(row_name)
		if row_index in self.ClosedRows:
			return False

		if row_index is None:
			return False
		
		self.Index.pop_index(row_index)
		self.PubSub.publish("Matrix changed!")
			
		if clear:
			self.Array[row_index] = np.zeros(1, dtype=self.DType) #might be TODO

		self.ClosedRows.add(row_index)
		if len(self.ClosedRows) >= self.MaxClosedRowsCapacity * self.Array.shape[0]:
			self.flush()
		
		crc = len(self.ClosedRows)
		self.Gauge.set("rows.active", self.Array.shape[0] - crc)
		self.Gauge.set("rows.closed", crc)
		return True


	def close_rows(self, row_names, clear=True):
		for name in row_names:
			self.close_row(name, clear=clear)


	def get_row_index(self, row_name: str):
		return self.Index.get_row_index(row_name)


	def get_row_name(self, row_index: int):
		return self.Index.get_row_name(row_index)


class NamedMatrix(NamedMatrixMixin):

	def __init__(self, app, dtype='float_', id=None, config=None):
		super().__init__(app, dtype=dtype, id=id, config=config)
		self.PubSub = asab.PubSub(app)


	def zeros(self):
		super().zeros()
		self.Index = Index()


	def serialize(self):		
		serialized = {}
		serialized['Index'] = self.Index.serialize()
		serialized['ClosedRows'] =self.ClosedRows.serialize()
		serialized['DType'] = self.DType
		serialized['Array'] = self.Array.tolist()
		return serialized


	def deserialize(self, data):
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


class PersistentNamedMatrix(NamedMatrixMixin, PersistentMatrix):

	def zeros(self):
		super().zeros()
		path  = os.path.join(self.Path, 'map.dat')
		self.Index = PersistentIndex(path, self.Array.shape[0])

