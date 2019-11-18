import numpy as np
import logging

from .timewindowanalyzer import TimeWindowAnalyzer

###

L = logging.getLogger(__name__)

###


class ThresholdAnalyzer(TimeWindowAnalyzer):

	"""

	Threshold Analyzer is based on TimeWindowAnalyzer and detects, if any
	monitored value exceeded or subceeded the preconfigured bounds.
	This analyzer can be used also only through configuration.

	predicate method - Check whether event contains related attributes

	evaluate method - Take event attributes and sorts them into the matrix

	analyze method - Check whether any value in the matrix is over the preconfigured bounds and if so, call the alarm.
				To analyze, whether the values are out of bounds, the 'np.where()' method is used. It pass the
				position of values out of bounds within the matrix to the alarm method.
				x = row position, y = column position

	alarm method - Return arguments

...

	Threshold settings:
		exceedance >>> if 'lower_bound' is set to '-inf' and upper_bound is not set to 'inf', then alarm is called when
						any value in matrix exceed upper_bound

		subceedance >>> if lower_bound is not set to '-inf' and upper_bound is set to 'inf', then alarm is called when
						any value in matrix subceed lower_bound

		range >>> if lower_bound is not set to '-inf' and upper_bound is not set to 'inf', then alarm is called when
					any value in matrix is out of preconfigured range

	"""

	ConfigDefaults = {

		'event_attribute': '', # Name of the attribute, e.g. server name
		'event_value': '', # Name of the attribute values to load into the matrix and to be used for
						   # analyzing, e.g. server overload values
		'lower_bound': '-inf', # Lower bound of the threshold
		'upper_bound': 'inf', # Upper bound of the threshold
		'analyze_period': 300, # Launch period of analyze method

	}

	def __init__(self, app, pipeline, id=None, config=None):

		super().__init__(app, pipeline, matrix_id=None, dtype='float_', columns=15, analyze_on_clock=True,
						 resolution=60, start_time=None, clock_driven=True, id=id, config=config)

		self.EventAttribute = self.Config['event_attribute']
		self.EventValue = self.Config['event_value']
		self.Lower = float(self.Config['lower_bound'])
		self.Upper = float(self.Config['upper_bound'])

		self.WarmingUpLimit = int()


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

		# Fill matrix with the values
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
		if self.Lower == float('-inf') and self.Upper != float('inf'):
			x, y = np.where((data > self.Upper) & warming_up)
			self.alarm(x, y)

		# Subceedance
		elif self.Lower != float('-inf') and self.Upper == float('inf'):
			x, y = np.where((data < self.Lower) & warming_up)
			self.alarm(x, y)

		# Range
		elif self.Lower != float('-inf') and self.Upper != float('inf'):
			x, y = np.where(((data < self.Lower) | (data > self.Upper)) & warming_up)
			self.alarm(x, y)


	def alarm(self, *args):
		pass

