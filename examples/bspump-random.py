import logging

import time

import bspump
import bspump.common
import bspump.random
import bspump.trigger

##


L = logging.getLogger(__name__)


##


class MyApplication(bspump.BSPumpApplication):
	def __init__(self):
		super().__init__()
		svc = self.get_service("bspump.PumpService")
		svc.add_pipeline(MyPipeline(self))


class MyPipeline(bspump.Pipeline):
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		upper_bound = int(time.time())
		lower_bound = upper_bound - 100500
		self.build(
			bspump.random.RandomSource(app, self, choice=['a', 'b', 'c'], config={
				'number': 5
			}).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=10)),

			bspump.random.RandomEnricher(app, self, config={
				'field': '@timestamp',
				'lower_bound': lower_bound,
				'upper_bound': upper_bound
			}),
			bspump.common.PPrintProcessor(app, self),
			bspump.random.RandomDrop(app, self),
			bspump.common.PPrintSink(app, self)
		)


if __name__ == '__main__':
	app = MyApplication()
	app.run()
