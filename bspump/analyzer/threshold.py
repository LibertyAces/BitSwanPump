import datetime
import numpy as np

import logging

from .timewindowanalyzer import TimeWindowAnalyzer

###

L = logging.getLogger(__name__)

###


class ThresholdAnalyzer(TimeWindowAnalyzer):

	ConfigDefaults = {

		'event_attribute': '',  # User defined value, e.g. server name
		'load_event': '', # User defined load to matrix TODO reconsider, if it has to be set by user - e.g. maybe only event_attribute is ok as a load
		# if lower bound != -inf and upper bound == inf: alarm is set when value is below lower bound,
		# if lower bound != -inf and upper bound > lower_bound: alarm is set when value is out of bounds
		'lower_bound': '-inf',
		'upper_bound': 'inf',
		'analyze_period': 300,

	}

	def __init__(self, app, pipeline, id=None, config=None):

		super().__init__(app, pipeline, matrix_id=None, dtype='float_', columns=10, analyze_on_clock=True,
						 resolution=20, start_time=None, clock_driven=True, id=id, config=config)

		self.EventAttribute = self.Config['event_attribute']
		self.Load = self.Config['load_event']
		self.Lower = float(self.Config['lower_bound'])
		self.Upper = float(self.Config['upper_bound'])
		self.WarmingUpLimit = int()


	# check if event contains related fields
	def predicate(self, context, event):
		if self.EventAttribute not in event:
			return False

		if "@timestamp" not in event:
			return False

		return True


	def evaluate(self, context, event):
		value = event[self.EventAttribute]
		time_stamp = event["@timestamp"]

		self.row = self.TimeWindow.get_row_index(value)
		if self.row is None:
			self.row = self.TimeWindow.add_row(value)


		# Find the column in timewindow matrix to fit in
		column = self.TimeWindow.get_column(time_stamp)
		if column is None:
			column = self.TimeWindow.get_column(time_stamp)

		# Load
		self.TimeWindow.Array[self.row, column] = event[self.Load]


	def analyze(self): #TODO set analyzing method
		# checking an empty array
		if self.TimeWindow.Array.shape[0] == 0:
			return

		# warming up the matrix
		self.WarmingUpLimit = self.TimeWindow.Columns - 1
		warming_up = self.TimeWindow.WarmingUpCount[self.row] <= self.WarmingUpLimit

		data = self.TimeWindow.Array[:, :]

		if self.Lower == float('-inf') and np.any(np.where((data >= self.Upper) & warming_up)): # exceedance
			L.warning(str(self.alarm()))
		elif self.Lower != float('-inf') and self.Upper == float('inf') and np.any(np.where((data <= self.Lower)
																							& warming_up)): # subceedance
			L.warning(str(self.alarm()))

		#TODO create range condition
		# # elif np.any(np.where(((data < self.Lower) | (data > self.Upper)) & warming_up)): # range
		# elif np.any(np.where((data <= self.Lower) & warming_up)) or np.any(np.where((data >= self.Upper) & warming_up)):
		# 	L.warning(str(self.alarm()))
		# 	print(self.Lower, np.any(np.where((data <= self.Lower) & warming_up)), np.ndarray.min((data)), 'lower')
		# 	print(self.Upper, np.any(np.where((data >= self.Lower) & warming_up)), np.ndarray.max((data)),'upper')
		# 	print('range')


	def alarm(self):
		alarm_result = str('Threshold has been out of bounds')
		return alarm_result

