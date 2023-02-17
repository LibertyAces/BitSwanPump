import logging

import bspump
import bspump.common
import bspump.declarative
import bspump.random
import bspump.trigger

##

L = logging.getLogger(__name__)

##


class VegetableCounterPipeline(bspump.Pipeline):
	"""
	The VegetableCounter example illustrates usage of BSPump declarative expression inside the DeclarativeProcessor.
	The expression consists of nested expressions, which together calculate count of vegetables inside the event,
	while adding extra radishes if the number of radishes is higher than two.
	"""


	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)

		# Load the declaration from YML file
		file = open("./data/declarative-input.yml")
		declaration = file.read()

		self.DeclarativeProcessor = bspump.declarative.DeclarativeProcessor(app, self, declaration)

		self.build(

			bspump.random.RandomSource(app, self, choice=[
				{"eggs": 2, "potatoes": 12, "carrots": 5, "garbage": "to be removed", "name": "xpotatoes", "meta": "Say,Good,Bye!"},
				{"potatoes": 10, "radishes": 5, "meat": 8, "name": "xpotatoes", "meta": "Say,Good,Bye!"},
				{"radishes": 20, "carrots": 4, "potatoes": 10, "name": "xpotatoes", "meta": "Say,Good,Bye!"}
			], config={"number": 5}).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=10)),
			self.DeclarativeProcessor,
			bspump.common.PPrintSink(app, self)
		)


class VegetableCounterApplication(bspump.BSPumpApplication):

	async def initialize(self):
		svc = self.get_service("bspump.PumpService")

		pipeline = VegetableCounterPipeline(self)
		await pipeline.DeclarativeProcessor.initialize()
		svc.add_pipeline(pipeline)

		pipeline.start()


if __name__ == '__main__':
	app = VegetableCounterApplication()
	app.run()
