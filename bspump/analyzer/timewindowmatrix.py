import time
import logging

import numpy as np

import asab
import collections

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

	def __init__(self, app, dtype='float_', start_time=None, resolution=60, columns=15, clock_driven=False, persistent=False, id=None, config=None):
		self.Columns = columns
		super().__init__(app, dtype=dtype, persistent=persistent, id=id, config=config)

		if start_time is None:
			start_time = time.time()

		start = (1 + (start_time // resolution)) * resolution
		if self.Persistent:
			path = os.path.join(self.Path, 'time_config.dat')
			self.TimeConfig = PersistentTimeConfig(path, resolution, columns, start)
			self.WarmingUpCount = PersistentWarmingUpCount(path, self.Array.shape[0])
		else:
			self.TimeConfig = TimeConfig(resolution, columns, start)
			self.WarmingUpCount = WarmingUpCount(self.Array.shape[0])

		if clock_driven:
			advance_period = resolution / 4
			self.Timer = asab.Timer(app, self.on_clock_tick, autorestart=True)
			self.Timer.start(advance_period)
		else:
			self.Timer = None

		self.ClockDriven = clock_driven

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

		self.TimeConfig.add_start(self.TimeConfig.get_resolution())
		self.TimeConfig.add_end(self.TimeConfig.get_resolution())

		if self.Array.shape[0] == 0:
			return

		column = np.zeros((self.Array.shape[0], 1,) + self.Array.shape[2:])
		if self.Persistent:
			array = np.zeros(self.Array.shape, dtype=self.DType)
			array[:] = self.Array[:]
		else:
			array = self.Array

		array = np.hstack((array, column))
		array = np.delete(array, 0, axis=1)

		if self.Persistent:
			self.Array = np.memmap(self.ArrayPath,  dtype=self.DType, mode='w+', shape=array.shape)
			self.Array[:] = array[:]
		else:
			self.Array = array

		open_rows = list(set(range(0, self.Array.shape[0])) - self.ClosedRows.get_rows()) #TODO
		self.WarmingUpCount.decrease(open_rows)


	def add_row(self, row_name):
		'''
			Adds new row with `row_id` to the matrix and sets `warming_up_count`.
		'''

		row_index = super().add_row(row_name)
		if self.Array.shape[0] != len(self.WarmingUpCount):
			self.WarmingUpCount.extend(self.Array.shape[0], self.Array.shape[1])
		else:
			self.WarmingUpCount.assign(row_index, self.Array.shape[1])

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

		column_idx = int((event_timestamp - self.TimeConfig.get_end()) // self.TimeConfig.get_resolution())

		# These are temporal debug lines
		if column_idx < 0:
			L.exception(
				"The column index {} is less then 0, {} event timestamp, {} start time, {} end time, {} resolution, {} num columns".format(
					column_idx, event_timestamp, self.TimeConfig.get_start(), 
					self.TimeConfig.get_end(), self.TimeConfig.get_resolution(), self.Array.shape[1])) #TODO
			raise

		if column_idx >= self.Array.shape[1]:
			L.exception(
				"The column index {} is more then columns number, {} event timestamp, {} start time, {} end time, {} resolution, {} num columns".format(
					column_idx, event_timestamp, self.TimeConfig.get_start(), 
					self.TimeConfig.get_end(), self.TimeConfig.get_resolution(), self.Array.shape[1])) #TDODO
			raise

		return column_idx


	def advance(self, target_ts):
		'''
			Advance time window (add columns) so it covers target `timestamp` (`target_ts`)
			Also, if `target_ts` is in top 75% of the last existing column, add a new column too.

			"target_ts" must always be in seconds

		.. code-block:: python

			--------------------|-----------
			target_ts  ^ >>>    |
								^
								Start
			------------------------------

		'''
		added = 0
		while True:
			dt = (self.TimeConfig.get_start() - target_ts) / self.TimeConfig.get_resolution()
			if dt > 0.25:
				break
			self.add_column()
			added += 1

		return added


	def close_row(self, row_index, clear=True):
		super().close_row(row_index, clear=clear)
		self.WarmingUpCount.assign(row_index, self.Array.shape[1])


	async def on_clock_tick(self):
		'''
			React on timer's tick and advance the window.
		'''

		target_ts = time.time()
		self.advance(target_ts)

