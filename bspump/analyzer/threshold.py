import datetime
import numpy as np

import logging

from .timewindowanalyzer import TimeWindowAnalyzer

###

L = logging.getLogger(__name__)

###


class ThresholdAnalyzer(TimeWindowAnalyzer):

	'''

	Threshold Analyzer is based on TimeWindowAnalyzer and detects, if any
	monitored value exceeded or subceeded the preconfigured bounds.
	This analyzer can be used only through configuration.

	predicate method - check whether event contains related attributes

	evaluate method - take event attributes and sorts them into the matrix

	analyze method - check whether any value in the matrix is over the preconfigured bounds and if so, calls the alarm

	alarm method - return string with alarm sentence

	Threshold settings:
		exceedance >>> if 'lower_bound' is set to '-inf', then alarm is called when any value in matrix exceed
						upper_bound

		subceedance >>> if lower_bound is not set to '-inf' and upper_bound is set to 'inf', then alarm is called when
						any value in matrix subceed lower_bound

		range >>> if lower_bound is not set to '-inf' and upper_bound is not set to 'inf', then alarm is called when
					any value in matrix is out of preconfigured range
	'''

	ConfigDefaults = {

		'event_attribute': '',  # User defined value, e.g. server name
		'load_event': '', # User defined load to matrix TODO reconsider, if it has to be set by user - e.g. maybe only event_attribute is ok as a load
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

		# Getting the row indices
		self.row = self.TimeWindow.get_row_index(value)
		if self.row is None:
			self.row = self.TimeWindow.add_row(value)


		# Find the column in timewindow matrix to fit in
		column = self.TimeWindow.get_column(time_stamp)
		if column is None:
			column = self.TimeWindow.get_column(time_stamp)

		# Load #TODO reconsider what to 'load' - It has to describe what needs to be stored in the event.
		self.TimeWindow.Array[self.row, column] = event[self.Load]


	def analyze(self): #TODO set analyzing method
		# checking an empty array
		if self.TimeWindow.Array.shape[0] == 0:
			return

		# warming up the matrix
		self.WarmingUpLimit = self.TimeWindow.Columns - 1
		warming_up = self.TimeWindow.WarmingUpCount[self.row] <= self.WarmingUpLimit

		data = self.TimeWindow.Array[:, :]

		# TODO reslove last 3-4 zero arrays, which messing up np.any and np.where methods, aka how to deal with the zeros
		# checking the exceedance condition
		if self.Lower == float('-inf') and np.any((data >= self.Upper) & warming_up):
			L.warning(str(self.alarm()))
		# checking the subceedance condition
		elif self.Lower != float('-inf') and self.Upper == float('inf') and np.any((data <= self.Lower) & warming_up):
			L.warning(str(self.alarm()))
		# checking the range condition
		elif np.any((data <= self.Lower) & warming_up) or np.any((data >= self.Upper) & warming_up):
			L.warning(str(self.alarm()))


	def alarm(self):
		alarm_result = str('Threshold has been out of bounds')
		return alarm_result

