import abc
import asab
import json
import logging
import numpy as np


###

L = logging.getLogger(__name__)

###


class Index(abc.ABC):
	def __init__(self, id=None):
		super().__init__()
		self.Id = id if id is not None else self.__class__.__name__

	def update(self, matrix):
		pass


	def serialize(self):
		return {
			'id': self.Id,
			'class': self.__class__.__name__,
		}

	@abc.abstractmethod
	def search(self, *args) -> set:
		pass



class BitMapIndex(Index):
	def __init__(self, column, matrix, id=None):
		'''
			Make sure, that column values are discreet.
			Also the creation procedure is relatively slow.
		'''
		super().__init__(id=id)
		self.Column = column
		self.BitMap = {}
		
		open_rows = list(matrix.I2NMap.keys())
		self.UniqueValues = list(np.unique(matrix.Array[self.Column][open_rows]))

		for u in self.UniqueValues:
			x = np.where(matrix.Array[self.Column] == u)   
			self.BitMap[int(u)] = set(x[0].tolist())

	
	def search(self, value):
		'''
			Returns set of matrix indexes.
		'''

		return set(self.BitMap.get(value, []))



	def update(self, matrix):
		open_rows = list(set(range(0, matrix.Array.shape[0])) - matrix.ClosedRows)
		unique_values = set(np.unique(matrix.Array[self.Column][open_rows]))
		set_difference_left = set(self.UniqueValues) - unique_values # there are some deleted vals
		set_difference_right = unique_values - set(self.UniqueValues) # there are some added vals
		
		if len(set_difference_left) != 0:
			for set_member in set_difference_left:
				self.BitMap.pop(set_member)

		if len(set_difference_right) != 0:
			for set_member in set_difference_right:
				x = np.where(matrix.Array[self.Column] == set_member)
				self.BitMap[int(set_member)] = set(x[0].tolist())

		self.UniqueValues = list(unique_values)


	def serialize(self):
		serialized_bitmap = {}
		for key in self.BitMap:
			serialized_bitmap[key] = list(self.BitMap[key])
		
		serialized = super().serialize()
		serialized.update({
			'bitmap': serialized_bitmap,
			'column': self.Column,
			})

		return serialized

	
	def deserialize(self, data):
		self.BitMap = {}
		self.Column = data['column']
		
		for key in data['bitmap']:
			self.BitMap[key] = set(data['bitmap'][key])
			
		self.UniqueValues = list(self.BitMap.keys())



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



