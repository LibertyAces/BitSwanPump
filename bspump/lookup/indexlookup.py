import abc
import json
import logging
from ..abc.lookup import Lookup
from ..analyzer.sessionmatrix import SessionMatrix

###

L = logging.getLogger(__name__)

###

class IndexLookup(Lookup):
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


	def serialize(self):
		serialized = {}
		serialized['Matrix'] = self.Matrix.serialize()
		
		# (json.dumps(serialized['Matrix']['I2NMap'])).encode('utf-8')
		# print('succcccces!!!!!')

		serialized['Indexes'] = {}
		for index in self.Indexes:
			serialized['Indexes'] = self.Indexes

		return (json.dumps(serialized)).encode('utf-8')


	def deserialize(self, data_json):
		data = json.loads(data_json.decode('utf-8'))
		self.Matrix.deserialize(data['Matrix'])
		self.Indexes = data.get('Indexes')


	def rest_get(self):
		rest = super().rest_get()
		rest['Indexes'] = self.Indexes
		rest['Matrix'] = self.Matrix.serialize()
		return rest


	def add_bitmap_index(self, column):
		'''
			Make sure, that column values are discreet.
			Also the procedure is relatively slow.
		'''
		self.Indexes[column] = BitMapIndex(self.Matrix, column)


	def add_range_tree_index(self, column_start, column_end):
		'''
			For range search. Columns is array, where ranges are specified.
			Make sure, that ranges are integer or real and don't overlap.
		'''
		self.Indexes[column_start] = TreeRangeIndex(self.Matrix, column_start, column_end)
		

	
	def add_value_tree_index(self, column):
		'''
			For ranges and real values
		'''
		pass

	# def update_bitmap_index(self, column):
	# 	pass

	# def update_tree_index(self, column):
	# 	pass
	
	def search(self, *args):
		raise NotImplementedError("Lookup '{}' search() method not implemented".format(self.Id))



class Index(abc.ABC):

	@abc.abstractmethod
	def search(self, *args) -> set:
		pass


class TreeRangeIndex(Index):
	def __init__(self, matrix, column_start, column_end):
		self.Matrix = matrix
		self.ColumnStart = column_start
		self.ColumnEnd = column_end
		ranges = set()
		
		unique_start = np.unique(self.Matrix.Array[column_start])
		ranges |= set(unique_start)
		unique_end = np.unique(self.Matrix.Array[column_end])
		
		assert(len(unique_start) == len(unique_end)) # ranges overlapping
		
		ranges |= set(unique_end)
		ranges = sorted(list(ranges))
		self.Root = self.sorted_array_to_bst(ranges)


	def search(self, value):
		root = self.Root
		while True:
			if root['data'] == value:
				return root.data # no!
			
			if root['data'] > value:

				l = root['left']
				if l is None:
					return root['data'] # no!
				else:
					root = l
			if root['data'] < value:
				r = root['right']
				if r is None:
					return root['data'] # no!
				else:
					root = r
		return set()

	def serialize(self):
		pass

	def sorted_array_to_bst(self, arr): 
		if not arr: 
			return None

		mid = int(len(arr) / 2)
		root = {'data': arr[mid], 'left':None, 'right': None}
		root['left'] = self.sorted_array_to_bst(arr[:mid]) 
		root['right'] = self.sorted_array_to_bst(arr[mid+1:]) 
		return root

class TreeValueIndex(Index):
	pass


class TreeOverlappingRangeIndex(Index):
	def _init__(self, matrix, column_start, column_end):
		pass

	def search(self, value):
		# search_start
		# search_end
		# intersect
		pass



def BitMapIndex(Index):
	def __init__(self, matrix, column):
		'''
			Make sure, that column values are discreet.
			Also the procedure is relatively slow.
		'''
		self.N2IMap = {}
		self.Column = column

		self.UniqueValues = np.unique(matrix.Array[self.Column])
	
		for u in self.UniqueValues:
			x = np.where(matrix.Array[self.Column] == u)   
			self.N2IMap[u] = x[0].tolist()

	
	def search(self, value):
		'''
			Returns set of matrix indexes.
		'''
		return set(self.N2IMap.get(value, []))


	def serialize(self):
		return self.N2IMap

	def deserialize(self, data):
		pass

