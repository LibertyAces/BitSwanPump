import logging

import time

import asab
from ..abc.processor import Processor

###

L = logging.getLogger(__name__)

###


class Analyzer(Processor):
	"""
	Description:

	:return:
	"""

	ConfigDefaults = {
		"analyze_period": 60,  # every 60 seconds
	}

	def __init__(self, app, pipeline, analyze_on_clock=False, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.AnalyzePeriod = float(self.Config['analyze_period'])
		self.AnalyzeOnClock = analyze_on_clock

		if analyze_on_clock:
			self.Timer = asab.Timer(app, self.on_clock_tick, autorestart=True)
			app.PubSub.subscribe("Application.run!", self.start_timer)
		else:
			self.Timer = None

	# Implementation interface

	def start_timer(self, event_type):
		"""
		Description:

		:return:
		"""
		self.Timer.start(self.AnalyzePeriod)

	def analyze(self):
		"""
		Description:

		:return:
		"""
		pass


	def evaluate(self, context, event):
		"""
		Description: The function which records the information from the event into the analyzed object.
			Specific for each analyzer.


		:return:
		"""
		pass


	def predicate(self, context, event):
		"""
		Description: This function is meant to check, if the event is worth to process.
			If it is, should return True.
			Specific for each analyzer, but default one always returns True.

		:return:
		"""
		return True


	def process(self, context, event):
		"""
		Description: The event passes through `process(context, event)` unchanged.
			Meanwhile it is evaluated.

		:return:
		"""
		if self.predicate(context, event):
			self.evaluate(context, event)

		return event


	async def on_clock_tick(self):
		"""
		Description: Run analyzis every tick.

		:return:
		"""
		t0 = time.perf_counter()
		self.analyze()
		self.Pipeline.ProfilerCounter['analyzer_' + self.Id].add('duration', time.perf_counter() - t0)
		self.Pipeline.ProfilerCounter['analyzer_' + self.Id].add('run', 1)
