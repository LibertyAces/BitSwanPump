import time
import logging

import numpy as np

import asab
import collections
import abc

from ..abc.matrix import MatrixABC


###

L = logging.getLogger(__name__)

###


class SessionMatrix(MatrixABC):

	def __init__(self, app, column_formats, column_names, id=None, config=None):
		column_formats.append("i8")
		column_names.append("@timestamp_start")
		column_formats.append("i8")
		column_names.append("@timestamp_end")	
		super().__init__(app, column_names, column_formats, id=id, config=config)

	
	def add_row(self, row_id, start_time):
		row = np.zeros(1, dtype={'names': self.ColumnNames, 'formats': self.ColumnFormats})
		self.Matrix = np.append(self.Matrix, row)
		row_counter = len(self.RowMap)
		self.RowMap[row_id] = row_counter
		self.RevRowMap[row_counter] = row_id
		self.Matrix[-1]["@timestamp_start"] = start_time


	def close_row(self, row_id, end_time):
		row_counter = self.RowMap.get(row_id)
		if row_counter is not None:
			self.ClosedRows.add(row_counter)
			self.Matrix[row_counter]["@timestamp_end"] = end_time
