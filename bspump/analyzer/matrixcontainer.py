import time
import logging

import numpy as np

import asab
import collections


###

L = logging.getLogger(__name__)

###



class MatrixContainer(object):
	'''
	Each column has name and type. Types can be identified from table:
	
	'b'	Byte	np.dtype('b')
	'i'	Signed integer	np.dtype('i4') == np.int32
	'u'	Unsigned integer	np.dtype('u1') == np.uint8
	'f'	Floating point	np.dtype('f8') == np.int64
	'c'	Complex floating point	np.dtype('c16') == np.complex128
	'S', 'a'	String	np.dtype('S5')
	'U'	Unicode string	np.dtype('U') == np.str_
	'V'	Raw data (void)	np.dtype('V') == np.void

	storage has structure:
	{
		"row_id0":{
			"storage_id0": object,
			...
		},
		...
	}
	
	It is possible to specify the column as a matrix with different dimension, the tuple (second_dim, third_dim, ...). 
	E.g: '(4, 3)i8' will create for each row the matrix 
	[0 0 0
	 0 0 0
	 0 0 0
	 0 0 0]

	'''


	def __init__(self, app, column_names, column_formats, id=None):
		self.ColumnNames = column_names
		self.ColumnFormats = column_formats
		
		self.RowMap = collections.OrderedDict()
		self.RevRowMap = collections.OrderedDict()
		self.Storage = {}
		self.ClosedRows = set()
		self.Matrix = np.zeros(0, dtype={'names':self.ColumnNames, 'formats':self.ColumnFormats})
		self.Id = id if id is not None else self.__class__.__name__


	def rebuild_rows(self, mode):	
		if mode == "full":
			self.RowMap = collections.OrderedDict()
			self.RevRowMap = collections.OrderedDict()
			self.Storage = {}
			self.ClosedRows = set()
			self.Matrix = np.zeros(0, dtype={'names':self.ColumnNames, 'formats':self.ColumnFormats})
			
		elif mode == "partial":
			new_row_map = collections.OrderedDict()
			new_rev_row_map = collections.OrderedDict()
			saved_indexes = []
			i = 0
			for key in self.RowMap.keys():
				value = self.RowMap[key]
				if value not in self.ClosedRows:
					new_row_map[key] = i
					new_rev_row_map[i] = key
					saved_indexes.append(value)
					i += 1
				else:
					if value in self.Storage:
						self.Storage.pop(value)
			new_matrix = self.Matrix[saved_indexes]
			self.Matrix = new_matrix
			self.RowMap = new_row_map
			self.RevRowMap = new_rev_row_map
			self.ClosedRows = set()
		else:
			L.warn("Unknown mode '{}'".format(mode))

	def get_row(self, row_name):
		return self.RowMap.get(row_name)



class TimeWindowMatrixContainer(MatrixContainer):
	'''
    ## Time window

    --> Columns (time dimension), column "width" = resolution
	+---+---+---+---+---+---+
	|   |   |   |   |   |   |
	+---+---+---+---+---+---+
	|   |   |   |   |   |   |
	+---+---+---+---+---+---+
	|   |   |   |   |   |   |
	+---+---+---+---+---+---+
	|   |   |   |   |   |   |
	+---+---+---+---+---+---+
	|   |   |   |   |   |   |
	+---+---+---+---+---+---+
	^                       ^
	End (past)   <          Start (== now)

	'''
	def __init__(self, app, tw_dimensions, tw_format, resolution, start_time=None, id=None):
		column_names = []
		column_formats = []
		column_names.append("time_window")
		column_formats.append(str(tw_dimensions) + tw_format)

		column_names.append("warming_up_count")
		column_formats.append("i8")

		super().__init__(app, column_names, column_formats, id=id)
		if start_time is None:
			start_time = time.time()

		self.Resolution = resolution
		self.Dimensions = tw_dimensions
		self.Format = tw_format

		self.Start = (1 + (start_time // self.Resolution)) * self.Resolution
		self.End = self.Start - (self.Resolution * self.Dimensions[0])

		svc = app.get_service("bspump.PumpService")
		self.Counters = svc.locate_metrics("EarlyLateEventCounter")
		


	def add_column(self):
		self.Start += self.Resolution
		self.End += self.Resolution

		if self.Matrix.shape[0] == 0:
			return

		column = np.zeros([self.Matrix["time_window"].shape[0], 1, self.Dimensions[1]])
		time_window = np.hstack((self.Matrix["time_window"], column))
		time_window = np.delete(time_window, 0, axis=1)

		self.Matrix["time_window"] = time_window
		self.Matrix["warming_up_count"] -= 1
		
		# Overflow prevention
		self.Matrix["warming_up_count"][self.Matrix["warming_up_count"] < 0] = 0

	
	def add_row(self, row_id):
		
		if row_id in self.RowMap:
			return
		if row_id is None:
			return

		row = np.zeros(1, dtype={'names': self.ColumnNames, 'formats': self.ColumnFormats})
		self.Matrix = np.append(self.Matrix, row)
		row_counter = len(self.RowMap)
		self.RowMap[row_id] = row_counter
		self.RevRowMap[row_counter] = row_id
		self.Matrix[-1]["warming_up_count"] = self.Dimensions[0]

	
	

	
	def get_column(self, event_timestamp):
		'''
		The timestamp should be provided in seconds
		'''

		if event_timestamp <= self.End:
			self.Counters.add('events.late', 1)
			return None

		if event_timestamp >= self.Start:
			self.Counters.add('events.early', 1)
			return None

		column_idx = int((event_timestamp - self.End) // self.Resolution)

		# assert(column_idx >= 0)
		# assert(column_idx < self.Dimensions[0])

		# These are temporal debug lines
		if column_idx < 0:
			L.exception("The column index {} is less then 0, {} event timestamp, {} start time, {} end time, {} resolution, {} num columns".format(column_idx, 
				event_timestamp, self.Start, self.End, self.Resolution, self.Dimensions[0]))
			raise

		if column_idx >= self.Dimensions[0]:
			L.exception("The column index {} is more then columns number, {} event timestamp, {} start time, {} end time, {} resolution, {} num columns".format(column_idx, 
				event_timestamp, self.Start, self.End, self.Resolution, self.Dimensions[0]))
			raise

		return column_idx

	
	def close_row(self, row_id):
		row_counter = self.RowMap.get(row_id)
		if row_counter is not None:
			self.ClosedRows.add(row_counter)


class SessionMatrixContainer(MatrixContainer):

	def __init__(self, app, column_formats, column_names, id=None):
		column_formats.append("i8")
		column_names.append("@timestamp_start")
		column_formats.append("i8")
		column_names.append("@timestamp_end")	
		super().__init__(app, column_names, column_formats, id=id)

	
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
			



