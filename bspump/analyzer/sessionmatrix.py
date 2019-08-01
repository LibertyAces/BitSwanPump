import time
import logging

import numpy as np

import asab
import collections
import abc

from ..matrix import NamedMatrix


###

L = logging.getLogger(__name__)

###


class SessionMatrix(NamedMatrix):
	'''
		Matrix, specific for `SessionAnalyzer`.
	
		There are two fields added:

			- `start_timestamp`: UNIX timestamp of the start of a session (if not 0)
			- `end_timestamp`: UNIX timestamp of the end of a session (if not 0)
	'''

	def __init__(self, app, dtype:list, id=None, config=None):
		dtype = dtype[:]
		dtype.extend([
			('start_timestamp', 'i8'),
			('end_timestamp', 'i8'),
		])
		super().__init__(app, dtype=dtype, id=id, config=config)

	
	def add_row(self, row_name, start_time=None):
		'''
			Adds new row with `row_id` to the matrix and assigns the `@timestamp_start`
			the `start_time`.
		'''

		row_index = super().add_row(row_name)
		if start_time is not None:
			self.Array[row_index]["start_timestamp"] = start_time
		return row_index


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
