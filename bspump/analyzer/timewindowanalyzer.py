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
	'''

	ConfigDefaults = {
		'columns': 15, 
		'third_dimension': 1,
		'resolution': 60, # Resolution (aka column width) in seconds
	}

	def __init__(self, app, pipeline, twa_configuration=None, start_time=None, clock_driven=True, time_windows=None, id=None, config=None):
		'''
		time_windows is dictionary with provided windows and labels.

		Labels are the names of multiple time windows, it should be an array of them. If labels are not specified,
		one time window will be created and labelled as self.TimeWindows['default'] and set self.TimeWindow as an alias.

		Dimension is an optional integer, specifying the length of 3rd dimension for all windows.

		Examples:
		a) labels=None, dimension=3 => one time window with shape (n, m, 3) will be created.
		d) labels=['1st', '2nd', '3rd'], dimension=[3, 5, 6] => 3 time windows with shapes (n_i, m_i, dim_i) will be
		created.

		twa_configuration = {"label0":{'dimensions': (15, 2), 'tw_format':'int'}, 
		"label1":{'dimensions': (10, 3), 'tw_format':'double'}

		'''

		super().__init__(app, pipeline, id, config)

		if time_windows is None:
			self._create_time_window_aggregations(app, pipeline, twa_configuration=twa_configuration, start_time=start_time)	
		else:
			if time_windows == {}:
				raise RuntimeError("time_windows cannot be an empty dictionary")
			self.TimeWindowAggregations = time_windows

		self.LabelDefault = list(self.TimeWindows.values())[0]
		self.TimeWindowAggregation = self.TimeWindowAggregations[self.LabelDefault]

		if clock_driven:
			self.Timer = asab.Timer(app, self._on_tick, autorestart=True)
			self.Timer.start(int(self.Config['resolution']) / 4) # 1/4 of the sampling
		else:
			self.Timer = None


	def _create_time_window_aggregations(self, app, pipeline, twa_configuration, start_time):
		self.TimeWindows = {}

		if twa_configuration is None:
			twa_configuration = {
				"default": {
					'dimensions': (self.Config['columns'], self.Config['third_dimension']), 
					'tw_format':'int'
				}
			}

		for label in twq_configuration.keys():
			self.TimeWindowAggregations[label] = TimeWindowAggregation(
				app,
				pipeline,
				dimensions=twa_configuration[label]['dimensions'],
				tw_format=twa_configuration[label]['tw_format'],
				start_time=start_time,
				resolution=int(self.Config['resolution']),
			)
		

	def advance(self, target_ts):
		'''
		Advance time window (add columns) so it covers target timestamp (target_ts)
		Also, if target_ts is in top 75% of the last existing column, add a new column too.

		------------------|-----------
		target_ts  ^ >>>  |
		                  ^ 
		                  Start

		'''
		
		for tw in self.TimeWindowAggregations.values():
			while True:
				dt = (tw.Start - target_ts) / tw.Resolution
				if dt > 0.25: break
				tw.add_column()


	async def _on_tick(self):
		target_ts = time.time()
		self.advance(target_ts)
