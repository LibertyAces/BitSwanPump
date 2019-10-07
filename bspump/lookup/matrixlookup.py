import abc
import asab
import json
import logging
import importlib
import numpy as np
from ..abc.lookup import Lookup
from ..analyzer.sessionmatrix import SessionMatrix

###

L = logging.getLogger(__name__)

###

class MatrixLookup(Lookup):
	'''
		Numpy Lookup
	'''

	def __init__(self, app, matrix_id=None, dtype='float_', id=None, config=None, lazy=False):
		
		super().__init__(app, id=id, config=config, lazy=lazy)
		self.Indexes = {}

		svc = app.get_service("bspump.PumpService")
		if matrix_id is None:
			s_id = self.Id + "Matrix"
			self.Matrix = SessionMatrix(app, dtype, id=s_id)
			svc.add_matrix(self.Matrix)
		else:
			self.Matrix = svc.locate_matrix(matrix_id)


	def search(self, condition, target_column):
		'''
			Default search, override if optimized with indexes
		'''
		x = np.where(condition)
		if len(x[0]) == 0:

			return None
		
		return np.asscalar(self.Matrix.Array[x[0]][target_column])


	def serialize(self):
		serialized = {}
		serialized['Matrix'] = self.Matrix.serialize()
		serialized['Indexes'] = {}
		for index in self.Indexes:
			serialized["Indexes"][index] = self.Indexes[index].serialize()
		
		return (json.dumps(serialized)).encode('utf-8')


	def deserialize(self, data_json):
		data = json.loads(data_json.decode('utf-8'))
		self.Matrix.deserialize(data['Matrix'])
		self.Indexes = {}
		indexes = data.get("Indexes", {})
		for index in indexes:
			module = importlib.import_module(indexes[index]["module"])
			index_class = getattr(module, indexes[index]["class"])
			ind = index_class.construct(indexes[index])
			self.Indexes[index] = ind


	def rest_get(self):
		rest = super().rest_get()
		rest['Matrix'] = self.Matrix.serialize()
		return rest


	def add_bitmap_index(self, column, id=None, config=None):
		'''
			Make sure, that column values are discreet.
			Also the procedure is relatively slow.
		'''
		index = BitMapIndex(column, matrix=self.Matrix, id=id, config=config)
		self.Indexes[index.Id] = index


	# def add_range_tree_index(self, column_start, column_end):
	# 	'''
	# 		For range search. Columns is array, where ranges are specified.
	# 		Make sure, that ranges are integer or real and don't overlap.
	# 	'''
	# 	self.Indexes[column_start] = TreeRangeIndex(self.Matrix, column_start, column_end)
		

	
	# def add_value_tree_index(self, column):
	# 	'''
	# 		For ranges and real values
	# 	'''
	# 	pass

	# def update_bitmap_index(self, column):
	# 	pass

	# def update_tree_index(self, column):
	# 	pass
	
	# def search(self, *args):
	# 	raise NotImplementedError("Lookup '{}' search() method not implemented".format(self.Id))



class Index(abc.ABC, asab.ConfigObject):
	def __init__(self, id=None, config=None):
		super().__init__("{}".format(id if id is not None else self.__class__.__name__), config=config)


	def serialize(self):
		return {
			'id': self.Id,
			'class': self.__class__.__name__,
			'module': self.__class__.__module__,
			'config': self.Config,
		}


	@abc.abstractmethod
	def search(self, *args) -> set:
		pass


# class TreeRangeIndex(Index):
# 	def __init__(self, matrix, column_start, column_end):
# 		self.Matrix = matrix
# 		self.ColumnStart = column_start
# 		self.ColumnEnd = column_end
# 		ranges = set()
		
# 		unique_start = np.unique(self.Matrix.Array[column_start])
# 		ranges |= set(unique_start)
# 		unique_end = np.unique(self.Matrix.Array[column_end])
		
# 		assert(len(unique_start) == len(unique_end)) # ranges overlapping
		
# 		ranges |= set(unique_end)
# 		ranges = sorted(list(ranges))
# 		self.Root = self.sorted_array_to_bst(ranges)


# 	def search(self, value):
# 		root = self.Root
# 		while True:
# 			if root['data'] == value:
# 				return root.data # no!
			
# 			if root['data'] > value:

# 				l = root['left']
# 				if l is None:
# 					return root['data'] # no!
# 				else:
# 					root = l
# 			if root['data'] < value:
# 				r = root['right']
# 				if r is None:
# 					return root['data'] # no!
# 				else:
# 					root = r
# 		return set()

# 	def serialize(self):
# 		pass

# 	def sorted_array_to_bst(self, arr): 
# 		if not arr: 
# 			return None

# 		mid = int(len(arr) / 2)
# 		root = {'data': arr[mid], 'left':None, 'right': None}
# 		root['left'] = self.sorted_array_to_bst(arr[:mid]) 
# 		root['right'] = self.sorted_array_to_bst(arr[mid+1:]) 
# 		return root

# class TreeValueIndex(Index):
# 	def __init__(self, matrix, column):
# 		self.UniqueValues = np.unique(matrix.Array[self.Column])
# 		self.MaxValue = np.max(self.UniqueValues)
# 		self.MinValue = np.min(self.UniqueValues)



# class TreeOverlappingRangeIndex(Index):
# 	def _init__(self, matrix, column_start, column_end):
# 		pass

# 	def search(self, value):
# 		# search_start
# 		# search_end
# 		# intersect
# 		pass



def BitMapIndex(Index):
	def __init__(self, column, matrix=None, bitmap=None, id=None, config=None):
		'''
			Make sure, that column values are discreet.
			Also the creation procedure is relatively slow.
		'''
		super().__init__(id=id, config=config)
		self.Column = column
		if matrix is None:
			assert(bitmap is None)
			
			self.BitMap = bitmap
			self.UniqueValues = list(self.BitMap.keys())
		else:
			self.BitMap = {}
			self.UniqueValues = list(np.unique(matrix.Array[self.Column]))

			for u in self.UniqueValues:
				x = np.where(matrix.Array[self.Column] == u)   
				self.BitMap[u] = set(x[0].tolist())

	
	def search(self, value):
		'''
			Returns set of matrix indexes.
		'''

		return set(self.BitMap.get(value, []))



	def update(self, matrix):
		unique_values = set(np.unique(matrix.Array[self.Column]))
		set_difference_left = set(self.UniqueValues) - unique_values # there are some deleted vals
		set_difference_right = unique_values - set(self.UniqueValues) # there are some added vals
		
		if len(set_difference_left) != 0:
			for set_member in set_difference_left:
				self.BitMapIndex.pop(set_member)

		if len(set_difference_right) != 0:
			for set_member in set_difference_right:
				x = np.where(matrix.Array[self.Column] == set_member)
				self.BitMapIndex[set_member] = set(x[0].tolist())

		self.UniqueValues = list(unique_values)


	def serialize(self):
		serialized = super().serialize()
		serialized.update({
			'bitmap': self.BitMap,
			'column': self.Column,
			})

		return serialized


	@classmethod
	def construct(cls, definition:dict):
		id_ = definition.get('id')
		config = definition.get('config')
		bitmap = definition.get('bitmap')
		column = definition.get('column')
		return cls(column, bitmap=bitmap, id=id_, config=config)

