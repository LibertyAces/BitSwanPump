import asyncio
from .trigger import Trigger

###

class OpportunisticTrigger(Trigger):
	
	'''
	This trigger tries to trigger the pump as frequenty as possible.
	It triggers immediatelly when possible, after each Source report completed cycle and in 5 sec. period (see chilldown period)
	'''

	def __init__(self, app, id=None, run_immediately=True, chilldown_period=5):
		super().__init__(app, id)

		self.Loop = app.Loop
		self.ChilldownPeriod = chilldown_period # Seconds

		if run_immediately:
			self.Loop.call_soon(self.on_tick)
		else:
			self.Loop.call_at(self.Loop.time() + self.Period, self.on_tick)


	def on_tick(self):
		now = self.Loop.time()
		self.Loop.call_at(now + self.ChilldownPeriod, self.on_tick)

		self.fire()


	def done(self, trigger_source):
		self.Loop.call_soon(self.on_tick)
