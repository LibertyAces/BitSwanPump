import time
import logging

import numpy as np

import asab

from ..abc.matrix import MatrixABC

###

L = logging.getLogger(__name__)

###


class TimeWindowMatrix(MatrixABC):
	'''
		Container, specific for `TimeWindowAnalyzer`.
		`tw_dimensions` is matrix dimensions parameter as the tuple `(column_number, third_dimension)`.
		Example: `(5,1)` will create the matrix with n rows, 5 columns and 1 additional third dimension.
		`tw_format` is the letter from the table + number:

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
		By default the `Matrix` contains 2 fields `time_window` with the main
		time matrix and `warming_up_counter`, the integer value for each row,
		indicating how "old" is the row.
		The main specific attributes are:
		`Start` is the starting timestamp of the first column of the matrix;
		`End` is the ending timestamp of the last column;
		`Resolution` is the width of the column in seconds.

	.. code-block:: python

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

	def __init__(self, app, tw_dimensions, tw_format, resolution, start_time=None, id=None, config=None):
		column_names = []
		column_formats = []
		column_names.append("time_window")
		column_formats.append(str(tw_dimensions) + tw_format)

		column_names.append("warming_up_count")
		column_formats.append("i8")

		super().__init__(app, column_names, column_formats, id=id, config=config)
		if start_time is None:
			start_time = time.time()

		self.Resolution = resolution
		self.Dimensions = tw_dimensions
		self.Format = tw_format

		self.Start = (1 + (start_time // self.Resolution)) * self.Resolution
		self.End = self.Start - (self.Resolution * self.Dimensions[0])

		metrics_service = app.get_service('asab.MetricsService')
		self.Counters = metrics_service.create_counter(
			"EarlyLateEventCounter",
			tags={
				'matrix': self.Id,
				'tw': "TimeWindow",
			},
			init_values={
				'events.early': 0,
				'events.late': 0,
			}
		)
		


	def add_column(self):
		'''
			Adds new time column to the matrix and deletes the first one, simulating
			the time flow. `Start` and `End` attributes are advanced as well. 
		'''

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
		'''
			Adds new row with `row_id` to the matrix and sets `warming_up_count`.
		'''

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
		return row_counter

	
	def get_column(self, event_timestamp):
		'''
			Returns the right column, where the timestamp fits.
			If if falls earlier or later, returns `None`.
			The timestamp should be provided in seconds.
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
		'''
			Puts the `row_id` to the `ClosedRows`.
		'''

		row_counter = self.RowMap.get(row_id)
		if row_counter is not None:
			self.ClosedRows.add(row_counter)
