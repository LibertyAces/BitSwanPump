from .trigger import Trigger


class OpportunisticTrigger(Trigger):

	'''
	This trigger tries to trigger the pump as frequenty as possible.
	It triggers immediatelly when possible, after each Source report completed cycle and in 5 sec. period (see chilldown period)
	'''

	def __init__(self, app, id=None, run_immediately=True, chilldown_period=5):
		super().__init__(app, id=id)
		self.ChilldownPeriod = chilldown_period  # Seconds

		app.PubSub.subscribe("Application.tick!", self.on_tick)

		if run_immediately:
			self.Loop.call_soon(self.on_tick)


	def pause(self, pause=True):
		super().pause(pause)
		if not self.Paused:
			self.Loop.call_soon(self.on_tick)


	def on_tick(self, event_type="simulated"):
		now = self.Loop.time()
		if (self.LastFireAt != 0) and (now < (self.LastFireAt + self.ChilldownPeriod)):
			return

		self.fire()


	def done(self, trigger_source):
		self.Loop.call_soon(self.on_tick)


	@classmethod
	def construct(cls, app, definition: dict):
		id = definition.get('id')
		run_immediately = definition.get('args', {}).get('run_immediately', True)
		chilldown_period = definition.get('args', {}).get('chilldown_period', 5)
		return cls(app, id=id, run_immediately=run_immediately, chilldown_period=chilldown_period)
