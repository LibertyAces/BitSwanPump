import datetime
import numpy as np

import logging

from .timewindowanalyzer import TimeWindowAnalyzer

###

L = logging.getLogger(__name__)

###


class ThresholdAnalyzer(TimeWindowAnalyzer):

	ConfigDefaults = {

		'event_name': '',  # User defined value, e.g. server name
		'load': '', # User defined load to matrix
		# if lower bound > upper bound: alarm is set when value is below lower bound,
		# if lower bound != 0 and upper bound > lower_bound: alarm is set when value is out of bounds
		'lower_bound': 0,
		'upper_bound': 1000,
		'analyze_period':300,

	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, matrix_id=None, dtype='float_', columns=15, analyze_on_clock=True,
						 resolution=60, start_time=None, clock_driven=True, id=id, config=config)


		self.Event_name = self.Config['event_name']
		self.Load = self.Config['load']
		self.Lower = self.Config['lower_bound']
		self.Upper = self.Config['upper_bound']

		self.TimeWindow.zeros() #initializing timewindow with zeros


	# check if event contains related fields
	def predicate(self, context, event):
		if self.Event_name not in event:
			return False

		if "@timestamp" not in event:
			return False

		return True


	def evaluate(self, context, event):
		value = event[self.Event_name]
		time_stamp = event["@timestamp"]

		row = self.TimeWindow.get_row_index(value)
		if row is None:
			row = self.TimeWindow.add_row(value)

		# Find the column in timewindow matrix to fit in
		column = self.TimeWindow.get_column(time_stamp)
		if column is None:
			column = self.TimeWindow.get_column(time_stamp)

		# Load
		self.TimeWindow.Array[row, column] = event[self.Load]


	def analyze(self): #TODO set analyzing method
		# checking an empty array
		if self.TimeWindow.Array.shape[0] == 0:
			return

		data = self.TimeWindow.Array[:, :]
		# Changing zero values to np.nan
		data[data == 0] = np.nan
		median_matrix_value = np.nanmedian(data[:, :])

		if self.Lower == 0 and median_matrix_value > self.Upper: # exceedance
			print(self.alarm(median_matrix_value))
		elif self.Lower != 0 and self.Lower > self.Upper and median_matrix_value < self.Lower: # subceedance
			print(self.alarm(median_matrix_value))
		elif self.Lower != 0 and self.Lower < self.Upper and (median_matrix_value < self.Lower or
															  median_matrix_value > self.Upper): # range (out of bounds)
			print(self.alarm(median_matrix_value))


	def alarm(self, value):
		alarm_result = str('Threshold has been subceeded / exceeded at {}'
						   .format(str(datetime.datetime.now())[:-7].replace(" ", "T"))
						   +' by value {}'.format(str(value)))
		return alarm_result
