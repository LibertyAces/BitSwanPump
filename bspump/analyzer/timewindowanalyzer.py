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
		'resolution': 60, # Resolution (aka column width) in seconds
	}

	def __init__(self, app, pipeline, tws_configuration=None, start_time=None, clock_driven=True, time_windows=None, id=None, config=None):
		'''
		time_windows is dictionary with provided windows and labels.

		Labels are the names of multiple time windows, it should be an array of them. If labels are not specified,
		one time window will be created and labelled as self.TimeWindows['default'] and set self.TimeWindow as an alias.

		Dimension is an optional integer, specifying the length of 3rd dimension for all windows.

		Examples:
		a) labels=None, dimension=3 => one time window with shape (n, m, 3) will be created.
		d) labels=['1st', '2nd', '3rd'], dimension=[3, 5, 6] => 3 time windows with shapes (n_i, m_i, dim_i) will be
		created.

		tws_configuration = {"label0":{'third_dimension': 2}, "label1":{'third_dimension': 3}}

		'''

		super().__init__(app, pipeline, id, config)

		if time_windows is None:
			self._create_time_windows(app, pipeline, tws_configuration=tws_configuration, start_time=start_time)	
		else:
			if time_windows == {}:
				raise RuntimeError("time_windows cannot be an empty dictionary")
			
			self.TimeWindows = time_windows
			self.TimeWindow = list(self.TimeWindows.values())[0]

		if clock_driven:
			self.Timer = asab.Timer(app, self._on_tick, autorestart=True)
			self.Timer.start(int(self.Config['resolution']) / 4) # 1/4 of the sampling
		else:
			self.Timer = None


	def _create_time_windows(self, app, pipeline, tws_configuration, start_time):
		self.TimeWindows = {}

		if tws_configuration is None:
			tws_configuration = {"default":{"third_dimension":1}}

		for label in tws_configuration.keys():
			self.TimeWindows[label] = TimeWindowCapture(
				app,
				pipeline,
				third_dimension=tws_configuration[label][third_dimension],
				start_time=start_time,
				resolution=int(self.Config['resolution']),
				columns=int(self.Config['columns'])
			)
		
		self.TimeWindow = self.TimeWindows[list(tws_configuration.keys())[0]]



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

	def close_row(self, row_id, label=None):
		if label is None:
			t = self.TimeWindow
		else:
			t = self.TimeWindows[label]
		
		t.close_row(row_id)


	def rebuild_sessions(self, mode, label=None):
		if label is None:
			s = self.SessionMatrix
		else:
			s = self.SessionMatrixes[label]

		s.rebuild_rows(mode)


	def advance(self, target_ts):
		'''
		Advance time window (add columns) so it covers target timestamp (target_ts)
		Also, if target_ts is in top 75% of the last existing column, add a new column too.

		------------------|-----------
		target_ts  ^ >>>  |
		                  ^ 
		                  Start

		'''
		# columns_added = 0
		
		for tw in self.TimeWindows.values():
			while True:
				dt = (self.Start - target_ts) / self.Resolution
				if dt > 0.25: break
				tw.add_column()
				# columns_added += 1


	async def _on_tick(self):
		target_ts = time.time()
		self.advance(target_ts)

