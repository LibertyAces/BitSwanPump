import time
import numpy as np

import logging

from .timewindowanalyzer import TimeWindowAnalyzer
from .timewindowmatrix import TimeWindowMatrix

###

L = logging.getLogger(__name__)

###

class ThresholdAnalyzer(TimeWindowAnalyzer):
	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, matrix_id=None, dtype='float_', columns=15, analyze_on_clock=False,
						 resolution=60, start_time=None, clock_driven=False, id=id, config=config)

		self.TimeWindow.zeros() #initializing timewindow with zeros


	def analyze(self):



	def evaluate(self, context, event):
		...


	def alarm(self):
		...