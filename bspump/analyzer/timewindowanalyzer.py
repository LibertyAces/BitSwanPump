import time
import logging

import numpy as np

import asab

from .analyzer import Analyzer

###

L = logging.getLogger(__name__)

###

class TimeWindow(object):

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

	def __init__(self, app, pipeline, start_time, third_dimension=1, resolution=60, columns=15):

		if start_time is None:
			start_time = time.time()

		self.Resolution = resolution
		self.Columns = columns

		self.ThirdDimension = third_dimension

		self.Start = (1 + (start_time // self.Resolution)) * self.Resolution
		self.End = self.Start - (self.Resolution * self.Columns)
		self.Matrix = None

		self.RowMap = {}
		self.RevRowMap = {}

		#to warm up
		self.WarmingUpRows = None


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

		if self.Matrix is None:
			return

		if self.ThirdDimension >= 2:
			column = np.zeros([len(self.RowMap), 1, self.ThirdDimension])
			self.Matrix = np.hstack((self.Matrix, column))
			self.Matrix = np.delete(self.Matrix, 0, axis=1)

		else:
			column = np.zeros([len(self.RowMap), 1])
			self.Matrix = np.hstack((self.Matrix, column))
			self.Matrix = np.delete(self.Matrix, 0, axis=1)

		#decrease warming up
		self.WarmingUpRows[:, 0] -= 1

	
	def add_row(self, row_name):
		rowcounter = len(self.RowMap)
		self.RowMap[row_name] = rowcounter
		self.RevRowMap[rowcounter] = row_name

		#and to warming up
		if self.ThirdDimension >= 2:
			row = np.zeros([1, self.Columns, self.ThirdDimension])
		else:
			row = np.zeros([1, self.Columns])
		
		warm_up = self.Columns * np.ones([1, 1])
		
		if self.Matrix is None:
			self.Matrix = row
			self.WarmingUpRows = warm_up
		else:
			self.Matrix = np.vstack((self.Matrix, row))
			self.WarmingUpRows = np.vstack((self.WarmingUpRows, warm_up))

	
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


	def advance(self, target_ts):
		'''
		Advance time window (add columns) so it covers target timestamp (target_ts)
		Also, if target_ts is in top 75% of the last existing column, add a new column too.

		------------------|-----------
		target_ts  ^ >>>  |
		                  ^ 
		                  Start

		'''
		columns_added = 0
		while True:
			dt = (self.Start - target_ts) / self.Resolution
			if dt > 0.25: break
			self.add_column()
			columns_added += 1
			# L.warn("Time window was shifted")

		return columns_added



###

class TimeWindowAnalyzer(Analyzer):
	'''
	This is the analyzer for events with a temporal dimension (aka timestamp).
	Configurable sliding window records events withing specified windows and implements functions to find the exact time slot.
	Timer periodically shifts the window by time window resolution, dropping previous events.
	'''

	ConfigDefaults = {
		'columns': 15,
		'resolution': 60, # Resolution (aka column width) in seconds
	}

	def __init__(self, app, pipeline, labels=None, dimension=None, start_time=None, clock_driven=True, time_windows=None, id=None, config=None):
		'''
		time_windows is dictionary with provided windows and labels.

		Labels are the names of multiple time windows, it should be an array of them. If labels are not specified,
		one time window will be created and labelled as self.TimeWindows['default'] and set self.TimeWindow as an alias.

		Dimension is an optional integer, specifying the length of 3rd dimension for all windows.

		Examples:
		a) labels=None, dimension=3 => one time window with shape (n, m, 3) will be created.
		b) labels=None, dimension=None => one time window with shape (n, m) will be created.
		c) labels=['1st', '2nd', '3rd'], dimension=None => 3 time windows with shapes (n_i, m_i) will be created.
		d) labels=['1st', '2nd', '3rd'], dimension=x => 3 time windows with shapes (n_i, m_i, x) will be
		created.
		'''

		super().__init__(app, pipeline, id, config)

		if (labels is not None) and (time_windows is not None):
			raise RuntimeError("There cannot be labels and time_window specified at the same time") 

		if time_windows is None:
			self._create_time_windows(app, pipeline, labels=labels, dimension=dimension, start_time=start_time)	
		else:
			if time_windows == {}:
				raise RuntimeError("time_windows cannot be an empty dictionary")
			
			self.TimeWindows = time_windows
			self.TimeWindow = list(self.TimeWindows.keys())[0]

		if clock_driven:
			self.Timer = asab.Timer(app, self._on_tick, autorestart=True)
			self.Timer.start(int(self.Config['resolution']) / 4) # 1/4 of the sampling
		else:
			self.Timer = None


	def _create_time_windows(self, app, pipeline, labels, dimension, start_time):
		
		self.TimeWindows = {}

		if (labels is None):
			labels = []
			labels.append("default")
		
		for i, label in enumerate(labels):
			if dimension is None:
				self.TimeWindows[label] = TimeWindow(
					app,
					pipeline,
					start_time=start_time,
					resolution=int(self.Config['resolution']),
					columns=int(self.Config['columns'])
				)
			else:
				self.TimeWindows[label] = TimeWindow(
					app,
					pipeline,
					third_dimension=dimension,
					start_time=start_time,
					resolution=int(self.Config['resolution']),
					columns=int(self.Config['columns'])
				)
		
		self.TimeWindow = self.TimeWindows[labels[0]]



	def get_column(self, event_timestamp, label=None):
		if label is None:
			return self.TimeWindow.get_column(event_timestamp)
		else:
			return self.TimeWindows[label].get_column(event_timestamp)


	def get_row(self, row_name, label=None):
		if label is None:
			return self.TimeWindow.get_row(row_name)		
		else:
			return self.TimeWindows[label].get_row(row_name)


	#Adding new row to a window
	def add_row(self, row_name, label=None):
		if label is None:
			self.TimeWindow.add_row(row_name)		
		else:
			self.TimeWindows[label].add_row(row_name)



	def advance(self, target_ts):
		for tw in self.TimeWindows.values():
			tw.advance(target_ts)


	async def _on_tick(self):
		target_ts = time.time()
		self.advance(target_ts)

