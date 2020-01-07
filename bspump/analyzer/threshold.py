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

	analyze method - Check whether any value in the matrix is over the preconfigured bounds and if so, check the
					occurrance of the symptom in the array and then possibly call the alarm.
					To analyze, whether the values are out of bounds, the 'np.where()' method is used. It pass the
					position of values out of bounds within the matrix to the alarm method.
					x = row position, y = column position
					To detect whether the symptom occurrance of the 'values out of bounds' is higher or equal, than number
					set in the configuration, an aggregation is used. Result of aggregation is the number of occurrences
					and indices of those values. It is then passed to the alarm method together with x and y arrays.

	alarm method - Configurable, takes arguments.

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

		'event_attribute': '',  # Name of the attribute, e.g. server name
		'event_value': '',  # Name of the attribute values to load into the matrix and to be used for
		# analyzing, e.g. server overload values
		'lower_bound': '-inf',  # Lower bound of the threshold
		'upper_bound': 'inf',  # Upper bound of the threshold
		'anomaly_occurrence': 1,  # Number of occurrences of anomaly in array
		'analyze_period': 300,  # Launch period of analyze method
	}

	def __init__(self, app, pipeline, id=None, config=None):

		super().__init__(app, pipeline, analyze_on_clock=True, clock_driven=True, id=id, config=config)

		self.EventAttribute = self.Config['event_attribute']
		self.EventValue = self.Config['event_value']
		self.Lower = float(self.Config['lower_bound'])
		self.Upper = float(self.Config['upper_bound'])
		self.SymptomOccurrence = int(self.Config['symptom_occurrence'])

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
			return

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

		# Subceedance
		elif self.Lower != float('-inf') and self.Upper == float('inf'):
			x, y = np.where((data < self.Lower) & warming_up)

		# Range
		elif self.Lower != float('-inf') and self.Upper != float('inf'):
			x, y = np.where(((data < self.Lower) | (data > self.Upper)) & warming_up)

		# No boundaries set
		else:
			raise ValueError('Boundaries of the threshold has not been set!')

		# Symptom occurrence detection
		try:
			# Setting previous value. When it is empty, further computation wont proceed.
			previous = x[0]
		except IndexError:
			return
		# Setting initial value to count
		count = 1
		for i in range(1, len(x)):
			# Setting actual value
			actual = x[i]
			# Checking, if previous value equals actual
			if actual == previous:
				count += 1
			else:
				# Checking whether count >= occurrence

				if count >= self.SymptomOccurrence:
					self.alarm(x, y, count, i - 1)
				count = 1
				previous = actual
			# Checking if count >= occurrence and if the loop is at its end
			if (count >= self.SymptomOccurrence) and (i + 1 == len(x)):
				self.alarm(x, y, count, i)


	def alarm(self, *args):
		pass
