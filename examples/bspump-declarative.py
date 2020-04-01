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

	FIELD -> obtains field from the event
	ASSIGN -> inserts field into the event
	ADD -> adds values of item expressions
	TOKEN -> a predefined value
	IF -> if clause with then and else expressions
	HIGHER -> if a number is higher than a given number
	"""

	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.random.RandomSource(app, self, choice=[
				{"eggs": 2, "potatoes": 12, "carrots": 5},
				{"potatoes": 10, "radishes": 5, "meat": 8},
				{"radishes": 20, "carrots": 4, "milk": 10}
			], config={"number": 5}).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=10)),
			bspump.declarative.DeclarativeProcessor(app, self, expression={
				"class": "ASSIGN",
				"field": "count",
				"token": {
					# Count all available vegetables in events
					"class": "ADD",
					"items": [
						{
							"class": "FIELD",
							"field": "potatoes",
							"source": "event.id",
							"default": 0
						},
						{
							"class": "FIELD",
							"field": "carrots",
							"source": "event.id",
							"default": 0
						},
						{
							"class": "FIELD",
							"field": "radishes",
							"source": "event.id",
							"default": 0
						},
						# It was a fruitful year! If there is more then two radishes, add extra 10!
						{
							"class": "IF",
							"if": {
								"class": "HIGHER",
								"items": [
									{
										"class": "FIELD",
										"field": "radishes",
										"source": "event.id",
										"default": 0
									},
									2
								]
							},
							"then": {
								"class": "TOKEN",
								"token": 10
							},
							"else": 0,
						},
						# BONUS: Add 20 extra salads!
						20
					]
				}
			}),
			bspump.common.PPrintSink(app, self)
		)


class VegetableCounterApplication(bspump.BSPumpApplication):

	def __init__(self):
		super().__init__()
		svc = self.get_service("bspump.PumpService")
		svc.add_pipeline(VegetableCounterPipeline(self))


if __name__ == '__main__':
	app = VegetableCounterApplication()
	app.run()
