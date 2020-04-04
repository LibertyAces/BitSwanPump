import logging

import bspump
import bspump.common
import bspump.declarative
import bspump.random
import bspump.trigger

##

L = logging.getLogger(__name__)

##


class DeclarativeParsingPipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.random.RandomSource(app, self, choice=[
				"one two three four five",
				"january february march april may",
				"dollar pound frank euro jen"
			], config={"number": 5}).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=10)),

			bspump.declarative.DeclarativeProcessor(app, self, expression={
				"function": "REGEX_PARSE",
				"regex": r"^(\w+)\s+(\w+)\s+(frank|march)?",
				"fields": ["A", "B", "C"],
				"value": { "function": "EVENT" }
			}),

			bspump.common.PPrintSink(app, self)
		)


class MyApplication(bspump.BSPumpApplication):

	def __init__(self):
		super().__init__()
		svc = self.get_service("bspump.PumpService")
		svc.add_pipeline(DeclarativeParsingPipeline(self))


if __name__ == '__main__':
	app = MyApplication()
	app.run()
