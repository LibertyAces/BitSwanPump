from bspump import BSPumpApplication, Pipeline
import bspump.trigger
import bspump.random
import bspump.common
import bspump.analyzer
import time
import numpy as np
import logging


##
L = logging.getLogger(__name__)
##

class MyApplication(BSPumpApplication):
	def __init__(self):
		super().__init__()
		svc = self.get_service("bspump.PumpService")
		matrix = MyTimeWindowMatrix(self, tw_dimensions=(100, 1), tw_format='i8', resolution=86400, id="MyMatrix")
		svc.add_matrix(matrix)
		svc.add_pipeline(MyPipeline0(self, matrix_id="MyMatrix"))
		svc.add_pipeline(MyPipeline1(self, matrix_id="MyMatrix"))
		

class MyPipeline0(Pipeline):
	def __init__(self, app, matrix_id, pipeline_id=None):
		super().__init__(app, pipeline_id)
		ub = int(time.time())
		lb = ub - 10000500
		self.build(
			bspump.random.RandomSource(app, self,
				config={'number': 50000, 'upper_bound':10000}
				).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=1)),
			bspump.random.RandomEnricher(app, self, config={'field':'@timestamp', 'lower_bound':lb, 'upper_bound': ub}), 
			MyTimeWindowAnalyzer(app, self, clock_driven=False, matrix_id=matrix_id),
			bspump.common.NullSink(app, self)
		)


class MyPipeline1(Pipeline):
	def __init__(self, app, matrix_id,pipeline_id=None):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.analyzer.AnalyzingSource(app, self, matrix_id=matrix_id).on(
				bspump.trigger.OpportunisticTrigger(app, chilldown_period=1)),
			bspump.common.NullSink(app, self)
		)


class MyTimeWindowAnalyzer(bspump.analyzer.TimeWindowAnalyzer):
	def evaluate(self, context, event):
		row = self.TimeWindow.get_row(event['id'])
		if row is None:
			# print("wa?", self.Matrix.shape, id(self.TimeWindow.Matrix['time_window']), id(self.Matrix))
			row = self.TimeWindow.add_row(event['id'])
			# print("aw?", self.Matrix.shape, row, id(self.TimeWindow.Matrix['time_window']), id(self.Matrix))

		column = self.TimeWindow.get_column(event['@timestamp'])
		if column is not None:
			# self.Matrix[row, column, 0] += 1
			self.TimeWindow.Matrix['time_window'][row, column, 0] += 1


class MyTimeWindowMatrix(bspump.analyzer.TimeWindowMatrix):
	async def analyze(self):
		print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Analyzing!")
		megaevent = []
		for i in range(0, self.Matrix.shape[0]):
			for j in range(0, self.Matrix['time_window'].shape[1]):
				event = {}
				event['id'] = self.get_row_id(i)
				# sum_events = np.sum(self.Matrix["time_window"][i, :, 0])
				event['sum'] = self.Matrix['time_window'][i, j, 0]

				megaevent.append(event)
		print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Done!")
		return megaevent



if __name__ == '__main__':
	app = MyApplication()
	app.run()
