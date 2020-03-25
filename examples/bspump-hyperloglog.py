import logging
import time
import bspump
import bspump.common
import bspump.random
import bspump.trigger
import bspump.aggregation
from bspump.aggregation.hyperloglog import HyperLogLog
import bspump.analyzer
import numpy as np

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
		lower_bound = 0
		upper_bound = 10**6

		self.build(
			bspump.random.RandomSource(app, self, choice=['a', 'b', 'c'], config={
				'number': 1000000
			}).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=1)),

			bspump.random.RandomEnricher(app, self, id="RE0", config={
				'field': 'value',
				'lower_bound': lower_bound,
				'upper_bound': upper_bound
			}),

			ConservativeUniqueCounter(app, self),
			HyperLogLogTimeWindowCounter(app, self, config={'analyze_period': 10}),		
			bspump.common.NullSink(app, self)
		)


class ConservativeUniqueCounter(bspump.Processor):
	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Values = set()
	
	def process(self, context, event):
		value = event['value']
		self.Values.add(value)		
		return event

	def analyze(self):
		return len(self.Values)



class HyperLogLogTimeWindowCounter(bspump.analyzer.SessionAnalyzer):

	def __init__(self, app, pipeline, id=None, config=None):
		self.HLLAggregator = HyperLogLog()
		super().__init__(app, pipeline, analyze_on_clock=True, dtype="({},)i2".format(self.HLLAggregator.m), id=id, config=config)
		self.Sessions.add_row("The one and only row")


	def evaluate(self, context, event):
		value = event['value']
		self.HLLAggregator.add(value, self.Sessions.Array[0, :])
		

	def analyze(self):
		svc = self.App.get_service("bspump.PumpService")
		conservative_processor = svc.locate("MyPipeline.ConservativeUniqueCounter")
		ground_truth = conservative_processor.analyze()
		hll_count = self.HLLAggregator.count(self.Sessions.Array[0, :])
		error = self.HLLAggregator.compute_error(ground_truth, hll_count)
		L.warning("Ground Truth is {}, HyperLogLog estimation is {}, error is {} %".format(ground_truth, hll_count, error))


if __name__ == '__main__':
	app = MyApplication()
	app.run()
