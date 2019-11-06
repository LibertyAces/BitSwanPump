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

	predicate method - Check whether event contains related attributes

	evaluate method - Take event attributes and sorts them into the matrix

	analyze method - Check whether any value in the matrix is over the preconfigured bounds and if so, calls the alarm

	alarm method - Return string with alarm sentence; allows additional arguments

...

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
		'event_value': '', # User defined load to matrix TODO reconsider, if it has to be set by user - e.g. maybe only event_attribute is ok as a load
		'lower_bound': '-inf',
		'upper_bound': 'inf',
		'analyze_period': 300,

	}

	def __init__(self, app, pipeline, id=None, config=None):

		super().__init__(app, pipeline, matrix_id=None, dtype='float_', columns=15, analyze_on_clock=True,
						 resolution=60, start_time=None, clock_driven=True, id=id, config=config)

		self.EventAttribute = self.Config['event_attribute']
		self.EventValue = self.Config['event_value']
		self.Lower = float(self.Config['lower_bound'])
		self.Upper = float(self.Config['upper_bound'])
		self.WarmingUpLimit = int()


	# Check if event contains related fields
	def predicate(self, context, event):
		if self.EventAttribute not in event:
			return False

		if "@timestamp" not in event:
			return False

		return True


	def evaluate(self, context, event):
		attribute = event[self.EventAttribute]
		time_stamp = event["@timestamp"]

		# Getting the row indices
		row = self.TimeWindow.get_row_index(attribute)
		if row is None:
			row = self.TimeWindow.add_row(attribute)

		# Find the column in timewindow matrix to fit in
		column = self.TimeWindow.get_column(time_stamp)
		if column is None:
			column = self.TimeWindow.get_column(time_stamp)

		# Load the value of the event
		self.TimeWindow.Array[row, column] = event[self.EventValue]


	def analyze(self):
		# Checking an empty array
		if self.TimeWindow.Array.shape[0] == 0:
			return

		data = self.TimeWindow.Array
		# Warming up the matrix to avoid procedures on not fully filled matrix and resizing warming_up dimension
		# to avoid ValueError when checking the conditions of exceedance/subceedance/range.
		self.WarmingUpLimit = self.TimeWindow.Columns - 1
		warming_up = np.resize(self.TimeWindow.WarmingUpCount <= self.WarmingUpLimit, data.shape)

		# Exceedance
		if (self.Lower == float('-inf') and self.Upper != float('inf')) and np.any((data >= self.Upper) & warming_up):
			L.warning(str(self.alarm()))
		# Subceedance
		elif (self.Lower != float('-inf') and self.Upper == float('inf')) and np.any((data <= self.Lower) & warming_up):
			L.warning(str(self.alarm()))
		# Range
		elif (self.Lower != float('-inf') and self.Upper != float('inf')) and np.any(((data <= self.Lower) |
																					  (data >= self.Upper)) & warming_up):
			L.warning(str(self.alarm()))


	def alarm(self, *args):
		alarm_result = str('Threshold is out of bounds!')
		return alarm_result

