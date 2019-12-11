from .trigger import Trigger

###


class RunOnceTrigger(Trigger):
	"""
	RunOnceTrigger is an obsolete trigger that should not be used.

	The following issues should be taken into consideration and need to be refactored in the future:
	1) RunOnceTrigger issues the application stop.
	2) The self.fire() event is triggered before the pipeline is_ready()
	"""

	def __init__(self, app, id=None):
		super().__init__(app, id)
		self.App = app
		self.Loop.call_soon(self.fire)


	def done(self, trigger_source):
		self.App.stop()
