import logging

from .analyzer import Analyzer
from ..matrix.timewindowmatrix import TimeWindowMatrix, PersistentTimeWindowMatrix

###

L = logging.getLogger(__name__)

###


class TimeWindowAnalyzer(Analyzer):
	'''
		This is the analyzer for events with a temporal dimension (aka timestamp).
		Configurable sliding window records events withing specified windows and implements functions to find the exact time slot.
		Timer periodically shifts the window by time window resolution, dropping previous events.

		`TimeWindowAnalyzer` operates over the `TimeWindowMatrix` object.

		`resolution`is how many seconds fit in one time cell, default value is `60`.
		`start_time` is a unix timestamp for time to start. Default value is `None`, which will be equivalent current time.
		`clock_driven` is a boolean parameter, specifying how the matrix should be advanced. If `True`, it advances on timer's tick,
		else manually. Default value is `True`.
		`matrix_id` is an id of `TimeWindowMatrix` object alternatively passed, if not provided, the new matrix will be created with and ID derived from the Analyzer Id
		`analyze_on_clock` enables enables analyzis by timer.

		If the `TimeWindowAnalyzer` is `clock_driven`, the time should be periodically shifted (`on_clock_tick()`). The same
		function runs analyzis, if it's enabled.
	'''


	def __init__(
		self, app, pipeline, matrix_id=None, dtype='float_',
		columns=15, analyze_on_clock=False, resolution=60,
		start_time=None, clock_driven=False, persistent=False, id=None, config=None
	):

		super().__init__(app, pipeline, analyze_on_clock=analyze_on_clock, id=id, config=config)
		svc = app.get_service("bspump.PumpService")
		if matrix_id is None:
			matrix_id = self.Id + "Matrix"
			if persistent:
				self.TimeWindow = PersistentTimeWindowMatrix(
					app,
					dtype=dtype,
					columns=columns,
					resolution=resolution,
					clock_driven=clock_driven,
					start_time=start_time,
					id=matrix_id,
					config=config,
				)
			else:
				self.TimeWindow = TimeWindowMatrix(
					app,
					dtype=dtype,
					columns=columns,
					resolution=resolution,
					clock_driven=clock_driven,
					start_time=start_time,
					id=matrix_id,
					config=config,
				)
			svc.add_matrix(self.TimeWindow)
		else:
			# locate
			self.TimeWindow = svc.locate_matrix(matrix_id)
