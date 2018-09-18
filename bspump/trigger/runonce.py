import asyncio
from .trigger import Trigger

###

class RunOnceTrigger(Trigger):
	
	'''
	This needs to be seriously refactor!
	1) Cannot issue the application stop.
	2) The self.fire() event can be triggered only when the pipeline is_ready()
	'''

	def __init__(self, app, id=None):
		super().__init__(app, id)
		self.App = app
		self.Loop.call_soon(self.fire)


	def done(self, trigger_source):
		self.App.stop()
