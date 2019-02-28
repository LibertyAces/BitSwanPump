import time
import logging

import numpy as np

import asab


###

L = logging.getLogger(__name__)

###



class Aggregation(object):
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


	def __init__(self, app, pipeline, column_names, column_formats):
		self.ColumnNames = column_names
		self.ColumnFormats = column_formats
		
		self.RowMap = {}
		self.RevRowMap = {}
		self.Storage = {}
		self.ClosedRows = set()
		self.Matrix = np.zeros(0, dtype={'names':self.ColumnNames, 'formats':self.ColumnFormats})


	def rebuild_rows(self, mode):	
		if mode == "full":
			self.RowMap = {}
			self.RevRowMap = {}
			self.Storage = {}
			self.ClosedRows = set()
			self.Matrix = np.zeros(0, dtype={'names':self.ColumnNames, 'formats':self.ColumnFormats})
			
		elif mode == "partial":
			new_row_map = {}
			new_rev_row_map = {}
			saved_indexes = []
			for key in self.RowMap.keys():
				value = self.RowMap[key]
				if value not in self.ClosedRows:
					new_row_map[key] = value
					new_rev_row_map[value] = key
					saved_indexes.append(value)
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



class TimeWindowAggregation(Aggregation):
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
	def __init__(self, app, pipeline, tw_dimensions, tw_format, resolution, start_time=None):
		column_names = []
		column_formats = []
		column_names.append("time_window")
		column_formats.append(str(tw_dimensions) + tw_format)

		column_names.append("warming_up_count")
		column_formats.append("i8")

		super().__init__(app, pipeline, column_names, column_formats)
		if start_time is None:
			start_time = time.time()

		self.Resolution = resolution
		self.Dimensions = tw_dimensions
		self.Format = tw_format

		self.Start = (1 + (start_time // self.Resolution)) * self.Resolution
		self.End = self.Start - (self.Resolution * self.Dimensions[0])

		metrics_service = app.get_service('asab.MetricsService')
		self.Counters = metrics_service.create_counter(
			"counters",
			tags={
				'pipeline': pipeline.Id,
				'tw': "TimeWindow",
			},
			init_values={
				'events.early': 0,
				'events.late': 0,
			}
		)


	def add_column(self):
		self.Start += self.Resolution
		self.End += self.Resolution

		if self.Matrix.shape[0] == 0:
			return

		column = np.zeros([len(self.RowMap), 1, self.Dimensions[1]])
		time_window = np.hstack((self.Matrix["time_window"], column))
		time_window = np.delete(time_window, 0, axis=1)

		self.Matrix["time_window"] = time_window
		self.Matrix["warming_up_count"] -= 1
		
		# Overflow prevention
		self.Matrix["warming_up_count"][self.Matrix["warming_up_count"] < 0] = 0

	
	def add_row(self, row_id):
		row = np.zeros(1, dtype={'names': self.ColumnNames, 'formats': self.ColumnFormats})
		self.Matrix = np.append(self.Matrix, row)
		row_counter = len(self.RowMap)
		self.RowMap[row_id] = row_counter
		self.RevRowMap[row_counter] = row_id
		self.Matrix[-1]["warming_up_count"] = self.Dimensions[0]

	
	def get_row(self, row_name):
		return self.RowMap.get(row_name)

	
	def get_column(self, event_timestamp):
		'''
		The timestamp should be provided in seconds
		'''

		if event_timestamp <= self.End:
			self.Counters.add('events.late', 1)
			return None

		if event_timestamp > self.Start:
			self.Counters.add('events.early', 1)
			return None

		column_idx = int((event_timestamp - self.End) // self.Resolution)

		assert(column_idx >= 0)
		assert(column_idx < self.Dimensions[0])
		return column_idx

	
	def close_row(self, row_id):
		row_counter = self.RowMap.get(row_id)
		if row_counter is not None:
			self.ClosedRows.add(row_counter)


class SessionAggregation(Aggregation):

	def __init__(self, app, pipeline, column_formats, column_names):
		column_formats.append("i8")
		column_names.append("@timestamp_start")
		column_formats.append("i8")
		column_names.append("@timestamp_end")	
		super().__init__(app, pipeline, column_names, column_formats)

	
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
			



