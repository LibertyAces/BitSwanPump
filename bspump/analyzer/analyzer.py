import logging

import time

import asab
from ..abc.processor import Processor

###

L = logging.getLogger(__name__)

###


class Analyzer(Processor):
	'''
		This is general analyzer interface, which can be the basement of different analyzers.
		`analyze_on_clock` enables analyzis by timer, which period can be set by `analyze_period` or
		`Config["analyze_period"]`.

		In general, the `Analyzer` contains some object, where it accumulates some information about events.
		Events go through analyzer unchanged, the information is recorded by `evaluate()` function.
		The internal object sometimes should be processed and sent somewhere (e.g. another pipeline),
		this process can be done by `analyze()` function, which can be triggered by time, pubsub or externally.
	'''

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
		self.Timer.start(self.AnalyzePeriod)

	def analyze(self):
		'''
			The main function, which runs through the analyzed object.
			Specific for each analyzer.
			If the analyzed object is `Matrix`, it is not recommended to iterate through the matrix row by row (or cell by cell).
			Instead use numpy fuctions. Examples:
			1. You have a vector with n rows. You need only those row indeces, where the cell content is more than 10.
			Use `np.where(vector > 10)`.
			2. You have a matrix with n rows and m columns. You need to find out which rows
			fully consist of zeros. use `np.where(np.all(matrix == 0, axis=1))` to get those row indexes.
			Instead `np.all()` you can use `np.any()` to get all row indexes, where there is at least one zero.
			3. Use `np.mean(matrix, axis=1)` to get means for all rows.
			4. Usefull numpy functions: `np.unique()`, `np.sum()`, `np.argmin()`, `np.argmax()`.
		'''
		pass


	def evaluate(self, context, event):
		'''
			The function which records the information from the event into the analyzed object.
			Specific for each analyzer.
		'''
		pass


	def predicate(self, context, event):
		'''
			This function is meant to check, if the event is worth to process.
			If it is, should return True.
			Specific for each analyzer, but default one always returns True.
		'''
		return True


	def process(self, context, event):
		'''
			The event passes through `process(context, event)` unchanged.
			Meanwhile it is evaluated.
		'''
		if self.predicate(context, event):
			self.evaluate(context, event)

		return event


	async def on_clock_tick(self):
		'''
			Run analyzis every tick.
		'''
		t0 = time.perf_counter()
		self.analyze()
		self.Pipeline.ProfilerCounter['analyzer_' + self.Id].add('duration', time.perf_counter() - t0)
		self.Pipeline.ProfilerCounter['analyzer_' + self.Id].add('run', 1)
