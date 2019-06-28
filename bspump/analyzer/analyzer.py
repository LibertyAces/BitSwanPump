import logging
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
		"analyze_period": 60, # every 60 seconds
	}

	def __init__(self, app, pipeline, analyze_on_clock=False, analyze_period=None, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		if analyze_period is None:
			self.AnalyzePeriod = int(self.Config['analyze_period'])
		else:
			self.AnalyzePeriod = analyze_period
		self.AnalyzeOnClock = analyze_on_clock
		
		if analyze_on_clock:
			self.Timer = asab.Timer(app, self.on_clock_tick, autorestart=True) 
			self.Timer.start(self.AnalyzePeriod)
		else:
			self.Timer = None


	## Implementation interface
	def analyze(self):
		'''
			The main function, which runs through the analyzed object.
			Specific for each analyzer.
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
		await self.analyze()

