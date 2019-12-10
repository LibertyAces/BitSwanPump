import abc
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

		return set(self.BitMap.get(str(value), []))



	def update(self, matrix):
		open_rows = list(matrix.I2NMap.keys())
		unique_values = set(np.unique(matrix.Array[self.Column][open_rows]))
		set_difference_left = set(self.UniqueValues) - unique_values  # there are some deleted vals
		set_difference_right = unique_values - set(self.UniqueValues)  # there are some added vals

		if len(set_difference_left) != 0:
			for set_member in set_difference_left:
				self.BitMap.pop(set_member)

		if len(set_difference_right) != 0:
			for set_member in set_difference_right:
				x = np.where(matrix.Array[self.Column] == set_member)
				self.BitMap[str(set_member)] = set(x[0].tolist())

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



class TreeRangeIndex(Index):
	def __init__(self, column_start, column_end, matrix, id=None):
		super().__init__(id=id)
		self.ColumnStart = column_start
		self.ColumnEnd = column_end
		ranges = set()

		open_rows = list(matrix.I2NMap.keys())
		unique_start = np.unique(matrix.Array[column_start][open_rows])
		ranges |= set(unique_start)
		unique_end = np.unique(matrix.Array[column_end][open_rows])
		ranges |= set(unique_end)

		assert(len(unique_start) == len(unique_end))  # ranges overlapping

		self.Ranges = sorted(list(ranges))

		self.MinValue = None
		self.MaxValue = None
		self.Tree = None

		if len(self.Ranges) != 0:
			self.MinValue = int(self.Ranges[0])
			self.MaxValue = int(self.Ranges[-1])

			self.Tree = self.sorted_array_to_bst(matrix, self.Ranges, [], [])


	def search(self, value):
		if self.Tree is None:
			return set()

		if (value < self.MinValue) or (value >= self.MaxValue):
			return set()

		subtree = self.Tree
		while True:
			node = subtree['node']
			if node is None:
				return set(subtree['indexes'])

			if value < node:
				subtree = subtree['left']
			else:
				subtree = subtree['right']

		return set()


	def sorted_array_to_bst(self, matrix, arr, path, mask):
		if not arr:
			mask_ = mask + [False]
			if np.any(mask):
				path_ = path + [float('inf')]
				true_values = np.array(path_)[np.array(mask_)]
				lower = max(true_values)
				false_values = np.array(path_)[~np.array(mask_)]
				upper = min(false_values)
				r = tuple([lower, upper])
			else:
				path_ = path + [-float('inf')]
				r = tuple([path_[-1], path_[-2]])

			condition = (matrix.Array[self.ColumnEnd] <= r[1]) & (matrix.Array[self.ColumnStart] >= r[0])
			indexes = np.where(condition)
			result = {
				'node': None,
				'indexes': indexes[0].tolist(),
				'left': None,
				'right': None
			}

			return result

		mid = int(len(arr) / 2)
		root = dict(node=int(arr[mid]), indexes=[])
		root['left'] = self.sorted_array_to_bst(matrix, arr[:mid], path + [arr[mid]], mask + [False])
		root['right'] = self.sorted_array_to_bst(matrix, arr[mid + 1:], path + [arr[mid]], mask + [True])
		return root


	def update(self, matrix):
		ranges = set()
		open_rows = list(matrix.I2NMap.keys())
		unique_start = np.unique(matrix.Array[self.ColumnStart][open_rows])
		ranges |= set(unique_start)
		unique_end = np.unique(matrix.Array[self.ColumnEnd][open_rows])
		ranges |= set(unique_end)

		# TODO: optimize this monster
		# if open_rows == self.OpenRows:
		# 	# partial update
		# 	# a) deleted values
		# 	# b) added values
		# 	# c) updated values, bug
		# else:
		# 	# full update

		assert(len(unique_start) == len(unique_end))  # ranges overlapping
		self.Ranges = sorted(list(ranges))

		self.MinValue = None
		self.MaxValue = None
		self.Tree = None

		if len(self.Ranges) != 0:
			self.MinValue = self.Ranges[0]
			self.MaxValue = self.Ranges[-1]
			self.Tree = self.sorted_array_to_bst(matrix, self.Ranges, [], [])


	def serialize(self):
		serialized = super().serialize()
		ranges = []
		for r in self.Ranges:
			ranges.append(int(r))

		serialized.update({
			'tree': self.Tree,
			'ranges': ranges,
			'column_start': self.ColumnStart,
			'column_end': self.ColumnEnd
		})
		return serialized


	def deserialize(self, data):
		self.Ranges = data['ranges']
		if len(self.Ranges) != 0:
			self.MinValue = self.Ranges[0]
			self.MaxValue = self.Ranges[-1]
		self.Tree = data['tree']
		self.ColumnStart = data['column_start']
		self.ColumnEnd = data['column_end']


class SliceIndex(Index):

	def __init__(self, column_start, column_end, matrix, resolution=None, id=None):
		super().__init__(id=id)
		self.ColumnStart = column_start
		self.ColumnEnd = column_end
		self.Resolution = resolution
		self.MinValue = None
		self.MaxValue = None
		self.SliceMap = None
		self._create_slices(matrix)


	def search(self, value):
		index = int((value - self.MinValue) // self.Resolution)
		key = self.MinValue + index * self.Resolution
		result = set(self.SliceMap.get(key, []))
		return result


	def update(self, matrix):
		print(">>>wawa")
		self._create_slices(matrix)
		print(len(self.SliceMap), self.MinValue, self.MaxValue, self.Resolution)


	def _create_slices(self, matrix):
		if matrix.Array.shape[0] == 0:
			return

		self.SliceMap = {}
		open_rows = list(matrix.I2NMap.keys())
		self.MinValue = float(np.min(matrix.Array[self.ColumnStart][open_rows]))
		self.MaxValue = float(np.max(matrix.Array[self.ColumnEnd][open_rows]))

		if self.Resolution is None:
			diffs = matrix.Array[self.ColumnEnd][open_rows] - matrix.Array[self.ColumnStart][open_rows]
			self.Resolution = float(np.min(diffs))

		start_value = self.MinValue

		while start_value < self.MaxValue:
			end_value = start_value + self.Resolution
			condition = (matrix.Array[self.ColumnEnd] >= end_value) & (matrix.Array[self.ColumnStart] <= start_value)
			indexes = np.where(condition)
			self.SliceMap[start_value] = indexes[0].tolist()
			start_value = end_value


	def serialize(self):
		serialized = super().serialize()
		serialized.update({
			'slice_map': self.SliceMap,
			'min_value': self.MinValue,
			'max_value': self.MaxValue,
			'resolution': self.Resolution,
			'column_start': self.ColumnStart,
			'column_end': self.ColumnEnd
		})
		return serialized


	def deserialize(self, data):
		# check how json works with float keys
		self.MinValue = data['min_value']
		self.MaxValue = data['max_value']
		self.Resolution = data['resolution']
		self.SliceMap = {}
		for key in data['slice_map']:
			self.SliceMap[float(key)] = data['slice_map'][key]

		self.Tree = data['tree']
		self.ColumnStart = data['column_start']
		self.ColumnEnd = data['column_end']
