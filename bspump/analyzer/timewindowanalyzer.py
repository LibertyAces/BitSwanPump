import time
import logging

import numpy as np

import asab

from .analyzer import Analyzer

###

L = logging.getLogger(__name__)

###

class TimeWindowAnalyzer(Analyzer):
	'''
	This is the analyzer for events with a temporal dimension (aka timestamp).
	Configurable sliding window records events withing specified windows and implements functions to find the exact time slot.
	Timer periodically shifts the window by time window resolution, dropping previous events.


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

	ConfigDefaults = {
		'warm_up_period': 15*60, # in seconds
		'columns': 356,
		'resolution': 60*60*24, # Resolution (aka column width) in seconds
	}

	def __init__(self, app, pipeline, start_time=None, clock_driven=True, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		
		if start_time is None:
			start_time = time.time()

		self.Resolution = int(self.Config['resolution'])
		self.Columns = int(self.Config['columns'])

		self.TimeWindowStart = (1 + (start_time // self.Resolution)) * self.Resolution
		self.TimeWindowEnd = self.TimeWindowStart - (self.Resolution * self.Columns)
		self.TimeWindow = None

		self.RowMap = {}
		self.RevRowMap = {}

		# Warm-up attribute
		self.WarmingUp = True
		self.WarmingUpTimer = asab.Timer(app, self._on_tick_warming_up)
		self.Timer.start(self.Config['warm_up_period'])

		metrics_service = app.get_service('asab.MetricsService')
		self.Counters = metrics_service.create_counter(
			"counters",
			tags={
				'pipeline': pipeline.Id,
				'twa': self.Id,
			},
			init_values={
				'events.early': 0,
				'events.late': 0,
			}
		)

		if clock_driven:
			self.Timer = asab.Timer(app, self._on_tick, autorestart=True)
			self.Timer.start(self.Resolution / 4) # 1/4 of the sampling
		else:
			self.Timer = None

	##

	def add_column(self):
		self.TimeWindowStart += self.Resolution
		self.TimeWindowEnd += self.Resolution

		if self.TimeWindow is None:
			return

		column = np.zeros([len(self.RowMap), 1])
		self.TimeWindow = np.hstack((self.TimeWindow, column))
		self.TimeWindow = np.delete(self.TimeWindow, 0, axis=1)


	def advance(self, target_ts):
		'''
		Advance time window (add columns) so it covers target timestamp (target_ts)
		Also, if target_ts is in top 75% of the last existing column, add a new column too.

		------------------|-----------
		target_ts  ^ >>>  |
		                  ^ 
		                  TimeWindowStart

		'''
		while True:
			dt = (self.TimeWindowStart - target_ts) / self.Resolution
			if dt > 0.25: break
			if dt < 0: print("Eeee!") # Target timestamp slipped in front of the window
			self.add_column()



	def get_column(self, event_timestamp):

		if event_timestamp < self.TimeWindowEnd:
			self.Counters.add('events.late', 1)
			return None

		if event_timestamp > self.TimeWindowStart:
			self.Counters.add('events.early', 1)
			return None

		column_idx = int((event_timestamp - self.TimeWindowEnd) // self.Resolution)

		assert(column_idx >= 0)
		assert(column_idx < self.Columns)
		
		return column_idx


	def get_row(self, row_name):
		return self.RowMap.get(row_name)


	#Adding new row to a window
	def add_row(self, row_name):
		rowcounter = len(self.RowMap)
		self.RowMap[row_name] = rowcounter
		self.RevRowMap[rowcounter] = row_name

		row = np.zeros([1, self.Columns])
		
		if self.TimeWindow is None:
			self.TimeWindow = row
		else:
			self.TimeWindow = np.vstack((self.TimeWindow, row))


	async def _on_tick(self):

		target_ts = time.time()
		self.advance(target_ts)
#		if not self.WarmingUp:
#			await self.analyze()
#		start = time.time()
		
#		end = time.time()
#		L.warn("Time window was shifted, it cost {:0.3f} sec".format(end-start))


	async def _on_tick_warming_up(self):
		self.WarmingUp = False
