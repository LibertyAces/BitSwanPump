import time
import logging

import numpy as np

import asab
import collections
import abc

from ..abc.matrix import NamedMatrixABC


###

L = logging.getLogger(__name__)

###


class SessionMatrix(NamedMatrixABC):
	'''
		Matrix, specific for `SessionAnalyzer`.
		`column_formats` is an array, each element contains the letter from the table + number:

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
		It is possible to create a matrix with elements of specified format. The tuple with number of dimensions should 
		stand before the letter.
		Example: '(6, 3)i8' will create the matrix with n rows, 6 columns and 3 third dimensions with integer elements.
		`column_names` is an array with names of each column, with the same length as `column_formats`.

	'''

	def __init__(self, app, column_formats, column_names, id=None, config=None):
		column_formats.append("i8")
		column_names.append("@timestamp_start")
		column_formats.append("i8")
		column_names.append("@timestamp_end")	
		super().__init__(app, column_names, column_formats, id=id, config=config)

	
	def add_row(self, row_name, start_time=None):
		'''
			Adds new row with `row_id` to the matrix and assigns the `@timestamp_start`
			the `start_time`.
		'''

		row_id = super().add_row(row_name)
		if start_time is not None:
			self.Matrix[-1]["@timestamp_start"] = start_time
		return row_id


	# def close_row(self, row_id, end_time=None):
	# 	'''
	# 		Puts the `row_id` to the ClosedRows and assigns the `@timestamp_end` the `end_time`.
	# 	'''

	# 	row_counter = self.RowMap.get(row_id)
	# 	if row_counter is not None:
	# 		self.ClosedRows.add(row_counter)
	# 		if end_time is not None:
	# 			self.Matrix[row_counter]["@timestamp_end"] = end_time
