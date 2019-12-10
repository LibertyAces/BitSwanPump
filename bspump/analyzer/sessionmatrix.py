import logging

from ..matrix.matrix import NamedMatrix

###

L = logging.getLogger(__name__)

###


class SessionMatrix(NamedMatrix):
	ConfigDefaults = {
		'primary_name': 'id'
	}

	'''
		Matrix, specific for `SessionAnalyzer`.

	'''

	def __init__(self, app, dtype='float_', id=None, config=None):
		if not isinstance(dtype, str):
			dtype = dtype[:]
		super().__init__(app, dtype=dtype, id=id, config=config)
		self.PrimaryName = self.Config['primary_name']


	def store(self, row_name: str, event):
		'''
			Store the event in the matrix.
			The event must prepared so that it matches a data type of the cell (dtype)
		'''
		row_index = self.get_row_index(row_name)
		if row_index is None:
			return False
		self.Array[row_index] = event



	def store_event(self, row_index: int, event, keys=None):
		if keys is None:
			keys = event.keys()

		names = self.Array.dtype.names
		if names is None:
			L.warning("The matrix does not have correct column-like dtype")
			raise

		for key in keys:
			if key in names:
				self.Array[row_index][key] = event[key]


	def decode_row(self, row_index: int, keys=None):

		if keys is None:
			keys = list(self.Array.dtype.names)

		if keys is None:
			L.warning("The matrix does not have correct column-like dtype")
			raise

		event = dict(zip(keys, self.Array[row_index][keys]))
		event[self.PrimaryName] = self.get_row_name(row_index)

		return event
