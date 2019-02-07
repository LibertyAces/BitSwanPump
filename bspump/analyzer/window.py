import time
import logging

import numpy as np

import asab

from .analyzer import Analyzer

###

L = logging.getLogger(__name__)

###


class Window(object):
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

	TODO: nums after letters??////?
	also dimensions!!!!!!!!!!!!!!!!!!
	'''

	def __init__(self, app, pipeline):
		self.RowMap = {}
		self.RevRowMap = {}
		self.ColumnNames = []
		self.ColumnFormats = []
		self.Storage = {}
		self.ClosedRows = set()
		self.Matrix = None


	def initialize_window(self):
		self.Matrix = np.zeros(0, dtype={'names':self.ColumnNames, 'formats':self.ColumnFormats})

	
	def add_row(self, row_id):
		row = np.zeros(1, dtype={'names': self.ColumnNames, 'formats': self.ColumnFormats})
		self.Matrix = np.append(self.Matrix, row)
		row_counter = len(self.RowMap)
		self.RowMap[row_id] = row_counter
		self.RevRowMap[row_counter] = row_id


	def rebuild_rows(self, mode):
		
		if mode == "full":
			self.initialize_window()
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

			new_sessions = self.Sessions[saved_indexes]
			self.Matrix = new_sessions
			self.RowMap = new_row_map
			self.RevRowMap = new_rev_row_map
			self.ClosedRows = set()
		else:
			L.warn("Unknown mode")



class TimeWindow(Window):
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
	def __init__(self, app, pipeline, start_time, tw_format='i30', third_dimension=1, resolution=60, columns=15):
		super().__init__(app, pipeline)
		if start_time is None:
			start_time = time.time()

		self.Resolution = resolution
		self.Columns = columns
		self.TWFormat = tw_format

		self.ThirdDimension = third_dimension

		self.Start = (1 + (start_time // self.Resolution)) * self.Resolution
		self.End = self.Start - (self.Resolution * self.Columns)

		self.ColumnNames.append("time_window")
		self.FormatNames.append("({},{}){}".format(self.Columns, self.ThirdDimension, self.TWFormat))

		self.ColumnNames.append("warming_up_count")
		self.FormatNames.append("i8")		

		self.initialize_window(self)

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

		if self.windowMatrix.shape[0] == 0:
			return

		column = np.zeros([len(self.RowMap), 1, self.ThirdDimension])
		time_window = np.hstack((self.Matrix["time_window"], column))
		time_window = np.delete(time_window, 0, axis=1)

		self.Matrix["time_window"] = time_window
		self.Matrix["warming_up_count"] -= 1
		# overflow prevent
		self.Matrix["warming_up_count"][self.Matrix["warming_up_count"] < 0] = 0

	
	def add_row(self, row_name):
		super().add_row()
		self.Matrix[-1]["warming_up_count"] = self.Columns

	
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
		assert(column_idx < self.Columns)
		return column_idx

	def close_row(self, row_id):
		row_counter = self.RowMap.get(row_id)
		if row_counter is not None:
			self.ClosedRows.add(row_counter)


class SessionWindow(Window):
	def __init__(self, app, pipeline, column_formats, column_names, id=None, config=None):
		super().__init__(app, pipeline)

		self.ColumnNames.append("@timestamp_start")
		self.ColumnFormats.append('i4')

		self.ColumnNames.append("@timestamp_end")
		self.ColumnFormats.append('i4')

		self.ColumnNames.extend(column_names)
		self.ColumnFormats.extend(column_formats)

	
	def add_row(self, session_id, start_time):
		super().add_row()
		self.Matrix[-1]["@timestamp_start"] = start_time


	def close_row(self, row_id, end_time):
		row_counter = self.RowMap.get(row_id)
		if row_counter is not None:
			self.ClosedRows.add(row_counter)
			self.Matrix[row_counter]["@timestamp_end"] = end_time



