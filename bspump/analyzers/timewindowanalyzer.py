import abc
import datetime
import logging
import time

import numpy as np

from .analyzer import Analyzer
import asab

###

L = logging.getLogger(__name__)

###

class TimeWindowAnalyzer(Analyzer):
	'''
	This is the analyzer for events with timestamp.
	Configurable sliding window records events withing specified windows and
	implements functions to find the exact time slot.
	Timer periodically shifts the window by time window resolution, dropping
	previous events   
	'''

	ConfigDefaults = {
		'start_time': int(time.time()*1000),
		'windows_size': 1200, # Window size in seconds (20 minutes)
		'resolution': 60, # Time slot resolution in seconds
		'analyze_windows_size' : 1200, # Might be different from window size
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		
		self.TimeWindowsStart = None
		self.TimeWindowsEnd = None
		self.set_time_windows_start_end(self.Config['start_time'])

		windows_size = self.Config['windows_size']
		analyze_windows_size = self.Config['analyze_windows_size']
		resolution = int(self.Config['resolution'])

		self.ResolutionMillis = self.Config['resolution'] * 1000
		self.TimeColumnCount = int(windows_size / resolution)
		self.AnalyzeColumnCount = int(analyze_windows_size / resolution)

		self.RowMap = {}
		self.RevRowMap = {}
		self.RowsCounter = -1
		self.TimeWindows = None

		metrics_service = app.get_service('asab.MetricsService')
		self.Counters = metrics_service.create_counter("counters", tags={}, init_values={'events.early': 0, 'events.late': 0})

		self.Timer = asab.Timer(app, self.on_tick)
		self.Timer.start(self.Config['resolution'])


	##
	def _datetime_to_ts_millis(self, dt):
		return (dt - datetime.datetime(1970,1,1)).total_seconds() * 1000


	def _floor_millis_to_minutes(self, millis):
		return millis - (millis % (60000))

	# initializing time windows' start and end
	def set_time_windows_start_end(self, ts):
		ts = int(ts)
		self.TimeWindowsStart = self._floor_millis_to_minutes(ts)
		self.TimeWindowsEnd = self._floor_millis_to_minutes(ts) + self.Config['windows_size']*1000


	# shift time windows
	def advance_time_windows(self):
		
		self.TimeWindowsStart += self.ResolutionMillis
		self.TimeWindowsEnd += self.ResolutionMillis

		if self.TimeWindows is None:
			return

		column = np.zeros([self.RowsCounter + 1, 1])
		self.TimeWindows = np.hstack((self.TimeWindows, column))
		self.TimeWindows = np.delete(self.TimeWindows, 0, axis=1)

		

	def get_time_column_index(self, event_timestamp):
		column_idx = int((event_timestamp - self.TimeWindowsStart) / self.ResolutionMillis)
		
		print(event_timestamp)
		if column_idx >= self.TimeColumnCount:
			#print('a1')
			self.Counters.add('events.late', 1)
			return None

		elif column_idx < 0:
			#print('a2')
			self.Counters.add('events.early', 1)
			return None

		else:
			return column_idx

	
	def get_time_column_indexes(self, event_timestamp, duration):
		
		if duration is None:
			idx = self.get_time_column_index(event_timestamp)
			if idx is None:
				return []
			else:
				return [idx]

		column_idx_start = int((event_timestamp - self.TimeWindowsStart) / self.ResolutionMillis)
		event_end_timestamp = (event_timestamp + duration * 1000)
		column_idx_end = int((event_end_timestamp - self.TimeWindowsStart) / self.ResolutionMillis)
		idxs = []

		if column_idx_start >= self.TimeColumnCount:
			self.Counters.add('events.late', 1)
			return idxs

		elif column_idx_start < 0:
			start = 0

		else:
			start = column_idx_start
		

		if column_idx_end < 0:
			self.Counters.add('events.early', 1)
			return idxs

		if column_idx_start == column_idx_end:
			idxs.append(column_idx_start)
			
		elif column_idx_end >= self.TimeColumnCount:
			idxs = list(range(start, self.TimeColumnCount))
			
		else:
			idxs = list(range(start, column_idx_end))
		
		return idxs


	###

	async def on_tick(self):
		await self.analyze()
		start = time.time()
		self.advance_time_windows()
		end = time.time()
		L.warn("Time window was shifted, it cost {} sec".format(end-start))
		self.Timer.start(self.Config['resolution'])


	#Adding new row to time window matrix and new entry to row_name2index dictionary
	def add_row_to_time_windows(self, row_name):
		self.RowsCounter += 1
		self.RowMap[row_name] = self.RowsCounter
		self.RevRowMap[self.RowsCounter] = row_name

		row = np.zeros([1, self.TimeColumnCount])
		
		if self.TimeWindows is None:
			self.TimeWindows = row
		else:
			self.TimeWindows = np.vstack((self.TimeWindows, row))

