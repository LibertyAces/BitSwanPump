import time
import logging

import numpy as np

import asab

from .analyzer import Analyzer
from .aggregation import TimeWindowAggregation

###

L = logging.getLogger(__name__)

###


class TimeWindowAnalyzer(Analyzer):
	'''
	This is the analyzer for events with a temporal dimension (aka timestamp).
	Configurable sliding window records events withing specified windows and implements functions to find the exact time slot.
	Timer periodically shifts the window by time window resolution, dropping previous events.
	'''

	ConfigDefaults = {
		'resolution': 60, # Resolution (aka column width) in seconds
	}

	def __init__(self, app, pipeline, tw_format='f8', tw_dimensions=(15,1), resolution=60, start_time=None, clock_driven=True, time_window=None, id=None, config=None):
		
		'''
		TimeWindowAnalyzer operates over the TimeWindowAggregation object. It requires
		tw_dimensions parameter as the tuple (column_number, third_dimension), format in form
		'b'	Byte	np.dtype('b')
		'i'	Signed integer	np.dtype('i4') == np.int32
		'u'	Unsigned integer	np.dtype('u1') == np.uint8
		'f'	Floating point	np.dtype('f8') == np.int64
		'c'	Complex floating point	np.dtype('c16') == np.complex128
		'S', 'a'	String	np.dtype('S5')
		'U'	Unicode string	np.dtype('U') == np.str_
		'V'	Raw data (void)	np.dtype('V') == np.void
		Example: 'i8' stands for int64.
		It also requires resolution, how many seconds fit in one time cell, default value is 60.

		'''

		super().__init__(app, pipeline, id, config)
		if time_window is None:
			self.TimeWindow = TimeWindowAggregation(
				app,
				pipeline,
				tw_dimensions=tw_dimensions,
				tw_format=tw_format,
				resolution=resolution,
				start_time=start_time
			)	
		else:
			self.TimeWindow = time_window

		if clock_driven:
			self.Timer = asab.Timer(app, self._on_tick, autorestart=True)
			self.Timer.start(int(self.Config['resolution']) / 4) # 1/4 of the sampling
		else:
			self.Timer = None

		

	def advance(self, target_ts):
		'''
		Advance time window (add columns) so it covers target timestamp (target_ts)
		Also, if target_ts is in top 75% of the last existing column, add a new column too.

		------------------|-----------
		target_ts  ^ >>>  |
		                  ^ 
		                  Start

		'''
		
		while True:
			dt = (self.TimeWindow.Start - target_ts) / self.TimeWindow.Resolution
			if dt > 0.25: break
			self.TimeWindow.add_column()


	async def _on_tick(self):
		target_ts = time.time()
		self.advance(target_ts)
