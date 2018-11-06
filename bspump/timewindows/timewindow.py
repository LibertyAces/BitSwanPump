import abc
import datetime
import logging
import time
import os

import numpy as np

import bspump
import asab

###

L = logging.getLogger(__name__)

###

class TimeWindowAnalyzer(bspump.Processor):

	ConfigDefaults = {
		'start_time': int(time.time()*1000),
		'windows_size': 1200, # Window size in seconds (20 minutes)
		'resolution': 60, # Time slot resolution in seconds
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		
		self.TimeWindowsStart = None
		self.TimeWindowsEnd = None
		self.set_time_windows_start_end(self.Config['start_time'])

		windows_size = self.Config['windows_size']
		resolution = int(self.Config['resolution'])

		self.ResolutionMillis = self.Config['resolution'] * 1000
		self.TimeColumnCount = int(windows_size / resolution)

		self.RowMap = {}
		self.RevRowMap = {}
		self.RowsCounter = -1
		self.TimeWindows = None

		metrics_service = app.get_service('asab.MetricsService')
		self.Counters = metrics_service.create_counter("counters", tags={}, init_values={'events.early': 0, 'events.late': 0})

		self.Timer = asab.Timer(app, self.on_tick)
		self.Timer.start(self.Config['resolution'])


	## Implementation interface
	@abc.abstractmethod
	def set_time_windows(self):
		raise NotImplemented("")

	@abc.abstractmethod
	def predicate(self, event):
		raise NotImplemented("")

	@abc.abstractmethod
	async def analyze(self):
		raise NotImplemented("")

	@abc.abstractmethod
	def evaluate(self, event):
		raise NotImplemented("")

	##
	def _datetime_to_ts_millis(self, dt):
		return (dt - datetime.datetime(1970,1,1)).total_seconds() * 1000


	def _floor_millis_to_minutes(self, millis):
		return millis - (millis % (60000))


	def set_time_windows_start_end(self, ts):
		ts = int(ts)
		self.TimeWindowsStart = self._floor_millis_to_minutes(ts)
		self.TimeWindowsEnd = self._floor_millis_to_minutes(ts) + self.Config['windows_size']*1000


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
		
		if column_idx >= self.TimeColumnCount:
			self.Counters.add('events.late', 1)
			return None

		elif column_idx < 0:
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

	def process(self, context, event):
		if not self.predicate(event):
			return event

		self.evaluate(event)

		return event


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



	
