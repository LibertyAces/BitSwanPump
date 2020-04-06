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
	IF -> if clause with then and else expressions
	HIGHER -> if a number is higher than a given number
	UPDATE -> updates dictionary with multiple dictionaries
	"""


	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		self.build(

			bspump.random.RandomSource(app, self, choice=[
				{"eggs": 2, "potatoes": 12, "carrots": 5},
				{"potatoes": 10, "radishes": 5, "meat": 8},
				{"radishes": 20, "carrots": 4, "potatoes": 10}
			], config={"number": 5}).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=10)),

			bspump.declarative.DeclarativeProcessor(app, self, '''
--- !DICT
with: !EVENT
add:
  seen: True
  when: !NOW
  rotten_potatoes:
    !ITEM EVENT potatoes
  count:
    !ADD
    - !ITEM EVENT potatoes
    - !ITEM
      with: !EVENT
      item: carrots
      default: 0
    - !IF
      is:
        !GT
        - !ITEM
          with: !EVENT
          item: radishes
          default: 0
        - 2
      then: !!float 10
      else: 0
    - 20
'''
),
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
