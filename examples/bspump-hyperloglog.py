import logging
import time
import bspump
import bspump.common
import bspump.random
import bspump.trigger
import bspump.aggregation
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

		values = set()
		self.build(
			bspump.random.RandomSource(app, self, choice=['a', 'b', 'c'], config={
				'number': 1000000
			}).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=1)),

			bspump.random.RandomEnricher(app, self, id="RE0", config={
				'field': 'value',
				'lower_bound': lower_bound,
				'upper_bound': upper_bound
			}),

			ConservativeUniqueCounter(app, self, values,),
			HyperLogLogTimeWindowCounter(app, self, values, config={'analyze_period': 10}),
			
			bspump.common.NullSink(app, self)
		)


class ConservativeUniqueCounter(bspump.Processor):
	def __init__(self, app, pipeline, values, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		self.Values = values


	def process(self, context, event):
		value = event['value']
		self.Values.add(value)
		
		return event



class HyperLogLogTimeWindowCounter(bspump.analyzer.SessionAnalyzer):

	def __init__(self, app, pipeline, values, id=None, config=None):
		m = 2048
		super().__init__(app, pipeline, analyze_on_clock=True, dtype="({},)i2".format(m), id=id, config=config)
		
		self.HLLAggregator = bspump.aggregation.HyperLogLog(m)

		self.Sessions.add_row("The one and only row")
		self.Values = values


	def evaluate(self, context, event):
		value = event['value']
		self.HLLAggregator.add(value, self.Sessions.Array[0, :])
		

	def analyze(self):
		ground_truth = len(self.Values)

		hll_count = self.HLLAggregator.count(self.Sessions.Array[0, :])
		err = np.abs(hll_count - ground_truth) / ground_truth * 100
		L.warning("Ground Truth is {}, HyperLogLog estimation is {}, error is {} %".format(ground_truth, hll_count, err))


if __name__ == '__main__':
	app = MyApplication()
	app.run()
