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
}

class ThresholdAnalyzer(TimeWindowAnalyzer):
	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, matrix_id=None, dtype='float_', columns=15, analyze_on_clock=False,
						 resolution=60, start_time=None, clock_driven=False, id=id, config=config)

		self._resolution = int(self.Config['resolution'])
		self._event_name = self.Config['event_name']
		self._threshold = int(self.Config['threshold'])

		self.TimeWindow.zeros() #initializing timewindow with zeros


	# check if event contains related fields
	def predicate(self, context, event):
		if self._event_name not in event:
			return False

		if "@timestamp" not in event:
			return False

		return True


	def analyze(self): #TODO set analyzing method

		...
		#threshold_limiter = len(line v matrixu (row))
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
		self.TimeWindow.Array[row, column] += event[] #TODO set load event


	def alarm(self, len_threshold_limiter, len_threshold): #TODO set alarm
		if not int(len_threshold_limiter):
			raise ValueError

		if not int(len_threshold):
			raise ValueError

		alarm_val = str('Threshold has been exceeded by {} %'.format(abs(len_threshold_limiter-len_threshold) / len_threshold) * 100)
		print(alarm_val)