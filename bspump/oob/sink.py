import logging

from ..abc.sink import Sink

#

L = logging.getLogger(__name__)

#


class OOBESink(Sink):
	"""
    OOBESink allows you to perform long synchronous operations "out-of-band" e.g. out of the synchronous processing within the pipeline.

    The following diagram illustrates the architecture of the "out-of-band" module with OOBESink and OOBEEngine:

    Pipeline A (synchronous)
    +---+---+---+---+---+---+
    Source	Processors	OOBESink
    +---+---+---+---+---+---+
                            |
                        OOBEEngine (asynchronous)
                            |
                            Pipeline B (synchronous)
                            +---+---+---+---+---+---+---+
                            InternalSource  Processors  Sink
                            +---+---+---+---+---+---+---+
"""

	def __init__(self, app, pipeline, engine, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Engine = engine

		app.PubSub.subscribe("OOBEEngine.pause!", self._engine_throttle)
		app.PubSub.subscribe("OOBEEngine.unpause!", self._engine_throttle)


	def process(self, context, event):
		self.Engine.put(context, event)


	def _engine_throttle(self, event_name, engine):
		if engine != self.Engine:
			return

		if event_name == "OOBEEngine.pause!":
			self.Pipeline.throttle(self, True)
		elif event_name == "OOBEEngine.unpause!":
			self.Pipeline.throttle(self, False)
		else:
			raise RuntimeError("Unexpected event name '{}'".format(event_name))
