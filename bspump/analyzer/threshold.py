import time
import numpy as np

import logging

from .timewindowanalyzer import TimeWindowAnalyzer
from .timewindowmatrix import TimeWindowMatrix

###

L = logging.getLogger(__name__)

###

ConfigDefaults = {
	'resolution': 60,  # Resolution (aka column width) in seconds
	'event_name': '',
	'threshold': 1000, # Max number of events before exceeding
	'level':'above',
	'load': 'something', # User defined load to matrix
}

class ThresholdAnalyzer(TimeWindowAnalyzer):
	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, matrix_id=None, dtype='float_', columns=15, analyze_on_clock=False,
						 resolution=60, start_time=None, clock_driven=False, id=id, config=config)

		self._resolution = int(self.Config['resolution'])
		self._event_name = self.Config['event_name']
		self._threshold = int(self.Config['threshold'])
		self.Level = self.Config['level'] # alarm level
		self.Load = self.Config['load']
		self.AlarmDict = {} #alarm dictionary - use it in 
		self.TimeWindow.zeros() #initializing timewindow with zeros


	# check if event contains related fields
	def predicate(self, context, event):
		if self._event_name not in event:
			return False

		if "@timestamp" not in event:
			return False

		return True


	def analyze(self): #TODO set analyzing method
		# if value is in AlarmDict - hold/dont start the alarm, else: start the alarm
		...
		#threshold_limiter = len(line v matrixu (row))f

		# as a len_threshold analyzer use np. function!!

		if self.Level == self.alarm(len_threshold_limiter, len_threshold):
			#some alarm
			...
		else:
			#not alarm
			...

		while len(threshold_limiter) > self._threshold:
			self.alarm(len(threshold_limiter), self._threshold) #call alarm method



	def evaluate(self, context, event):
		value = event[self._event_name]  # server name e.g.
		time_stamp = event["@timestamp"] # time stamp of the event

		row = self.TimeWindow.get_row_index(value)
		if row is None:
			row = self.TimeWindow.add_row(value)

		# find the column in timewindow matrix to fit in
		column = self.TimeWindow.get_column(time_stamp)
		if column is None:
			return

		# load
		self.TimeWindow.Array[row, column] = event[self.Load] #TODO set load event


	def alarm(self, len_threshold_limiter, len_threshold): #TODO set alarm
		self.level_val = ''
		if not int(len_threshold_limiter):
			raise ValueError

		if not int(len_threshold):
			raise ValueError



		alarm_val = str('Threshold has been exceeded by {} %'.format(abs(len_threshold_limiter-len_threshold) / len_threshold) * 100)
		print(alarm_val)

		if len_threshold_limiter > len_threshold:
			self.level_val = 'above'
		else:
			self.level_val = 'below'

		return self.lev_val