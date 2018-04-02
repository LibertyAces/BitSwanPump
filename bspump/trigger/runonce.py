import asyncio
from .trigger import Trigger

###

class RunOnceTrigger(Trigger):
	

	def __init__(self, app, id=None):
		super().__init__(app, id)
		self.App = app
		self.App.Loop.call_soon(self.fire)


	def done(self):
		self.App.stop()
