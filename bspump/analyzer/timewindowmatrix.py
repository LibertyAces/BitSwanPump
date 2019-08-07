import time
import logging

import numpy as np

import asab

from ..matrix.matrix import NamedMatrix

###

L = logging.getLogger(__name__)

###


class TimeWindowMatrix(NamedMatrix):
	'''
		Container, specific for `TimeWindowAnalyzer`.

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

	def __init__(self, app, dtype:list, tw_dimensions=(15, 1), tw_format='f8', resolution=60, start_time=None, id=None, config=None):
		dtype = dtype[:]
		dtype.extend([
			('warming_up_count', 'i4'),
			('time_window', str(tw_dimensions) + tw_format),
		])
		super().__init__(app, dtype=dtype, id=id, config=config)
		
		if start_time is None: start_time = time.time()

		self.Resolution = resolution
		self.Start = (1 + (start_time // self.Resolution)) * self.Resolution
		self.End = self.Start - (self.Resolution * self.Dimensions[0])
		self.Dimensions = tw_dimensions
		self.Format = tw_format

		metrics_service = app.get_service('asab.MetricsService')
		self.Counters = metrics_service.create_counter(
			"EarlyLateEventCounter",
			tags={
				'matrix': self.Id,
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

		if self.Array.shape[0] == 0:
			return

		column = np.zeros([self.Array["time_window"].shape[0], 1, self.Dimensions[1]])
		time_window = np.hstack((self.Array["time_window"], column))
		time_window = np.delete(time_window, 0, axis=1)

		self.Array["time_window"] = time_window
		open_rows = list(set(range(0, self.Array["time_window"].shape[0])) - self.ClosedRows)
		self.Array["warming_up_count"][open_rows] -= 1
		
		# Overflow prevention
		self.Array["warming_up_count"][self.Array["warming_up_count"] < 0] = 0

	
	def add_row(self, row_name):
		'''
			Adds new row with `row_id` to the matrix and sets `warming_up_count`.
		'''

		row_index = super().add_row(row_name)
		self.Array[row_index]["warming_up_count"] = self.Dimensions[0]
		return row_index

	
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

	
	# def close_row(self, row_id):
	# 	'''
	# 		Puts the `row_id` to the `ClosedRows`.
	# 	'''

	# 	row_counter = self.RowMap.get(row_id)
	# 	if row_counter is not None:
	# 		self.ClosedRows.add(row_counter)
