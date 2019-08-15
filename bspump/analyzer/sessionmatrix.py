import time
import logging

import numpy as np

import asab
import collections
import abc

from ..matrix.matrix import NamedMatrix


###

L = logging.getLogger(__name__)

###


class SessionMatrix(NamedMatrix):
	'''
		Matrix, specific for `SessionAnalyzer`.
	
	'''

	def __init__(self, app, dtype:list, id=None, config=None):
		dtype = dtype[:]
		super().__init__(app, dtype=dtype, id=id, config=config)


	def store(self, row_name: str, event):
		'''
			Store the event in the matrix.
			The event must prepared so that it matches a data type of the cell (dtype)
		'''
		row_index = self.get_row_index(row_name)
		if row_index is None: return False
		self.Array[row_index] = event


	# def close_row(self, row_id, end_time=None):
	# 	'''
	# 		Puts the `row_id` to the ClosedRows and assigns the `@timestamp_end` the `end_time`.
	# 	'''

	# 	row_counter = self.RowMap.get(row_id)
	# 	if row_counter is not None:
	# 		self.ClosedRows.add(row_counter)
	# 		if end_time is not None:
	# 			self.Matrix[row_counter]["@timestamp_end"] = end_time
