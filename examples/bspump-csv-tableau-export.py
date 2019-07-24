from bspump import BSPumpApplication, Pipeline
import bspump.trigger
import bspump.random
import bspump.common
import bspump.analyzer
import bspump.file
import bspump.tableau
import time
import numpy as np
import logging
import random


##
L = logging.getLogger(__name__)
##

class MyApplication(BSPumpApplication):
	def __init__(self):
		super().__init__()
		svc = self.get_service("bspump.PumpService")
		svc.add_pipeline(PrimaryPipeline(self))
		# svc.add_pipeline(SecondaryPipelineCSVSession(self))
		# svc.add_pipeline(SecondaryPipelineTableauSession(self))
		# svc.add_pipeline(SecondaryPipelineCSVTimeWindow(self))
		svc.add_pipeline(SecondaryPipelineTableauTimeWindow(self))
		
		

class PrimaryPipeline(Pipeline):
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		ub = int(time.time())
		lb = ub - 10000500
		lb_0 = 0
		ub_0 = 3
		column_formats = ['U8', '(2,2)f8', 'i8']
		column_names = ['name', 'fractions', 'num']
		choice = ['a', 'b', 'c']
		self.build(
			bspump.random.RandomSource(app, self, choice=choice,
				config={'number': 500}
				).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=.1)),
			bspump.random.RandomEnricher(app, self, config={'field':'@timestamp', 'lower_bound':lb, 'upper_bound': ub}, id="RE0"),
			bspump.random.RandomEnricher(app, self, config={'field':'fraction', 'lower_bound':lb_0, 'upper_bound': ub_0}, id="RE1"),
			MySessionAnalyzer(app, self, column_formats, column_names, analyze_on_clock=False),
			MyTimeWindowAnalyzer(app, self, tw_dimensions=(10, 1), resolution=60*60*24, analyze_on_clock=False, clock_driven=False),
			bspump.common.NullSink(app, self)
		)


class SecondaryPipelineCSVTimeWindow(Pipeline):
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.common.MatrixSource(app, 
				self, 
				"MyTimeWindowAnalyzerMatrix").on(bspump.trigger.PubSubTrigger(app, "Export!")
			),
			bspump.common.TimeWindowMatrixExportCSVGenerator(app, self),
			# bspump.common.PPrintSink(app, self)
			bspump.file.FileCSVSink(app, self, config={'path':'tw.csv'})
		)

class SecondaryPipelineTableauTimeWindow(Pipeline):
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.common.MatrixSource(app, 
				self, 
				"MyTimeWindowAnalyzerMatrix").on(bspump.trigger.PubSubTrigger(app, "Export!")
			),
			bspump.tableau.TimeWindowMatrixExportTableauGenerator(app, self),
			bspump.tableau.FileTableauSink(app, self,config={'path':'tw.tde'}),
			# bspump.common.PPrintSink(app, self)
		)


class SecondaryPipelineCSVSession(Pipeline):
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.common.MatrixSource(app, 
				self, 
				"MySessionAnalyzerMatrix").on(bspump.trigger.PubSubTrigger(app, "Export!")
			),
			bspump.common.SessionMatrixExportCSVGenerator(app, self),
			# bspump.common.PPrintSink(app, self)
			bspump.file.FileCSVSink(app, self, config={'path':'sess.csv'})
		)

class SecondaryPipelineTableauSession(Pipeline):
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.common.MatrixSource(app, 
				self, 
				"MySessionAnalyzerMatrix").on(bspump.trigger.PubSubTrigger(app, "Export!")
			),
			bspump.tableau.SessionMatrixExportTableauGenerator(app, self),
			# bspump.common.PPrintSink(app, self)
			bspump.tableau.FileTableauSink(app, self,config={'path':'sess.tde'})
		)


class MySessionAnalyzer(bspump.analyzer.SessionAnalyzer):
	Translate = {
		'a':'abc',
		'b':'bcd',
		'c':'cdef',
	}


	def evaluate(self, context, event):
		row = self.Sessions.get_row_index(event['id'])
		if row is None:
			row = self.Sessions.add_row(event['id'], event['@timestamp'])

		self.Sessions.Matrix['name'][row] = self.Translate[event['id']]
		self.Sessions.Matrix['num'][row] += 1
		fraction = int(event['fraction'])
		if fraction == 0:
			self.Sessions.Matrix['fractions'][row, 0, 0] += 1
		elif fraction == 1:
			self.Sessions.Matrix['fractions'][row, 0, 1] += 1
		elif fraction == 2:
			self.Sessions.Matrix['fractions'][row, 1, 0] += 1
		elif fraction == 3:
			self.Sessions.Matrix['fractions'][row, 1, 1] += 1



class MyTimeWindowAnalyzer(bspump.analyzer.TimeWindowAnalyzer):

	def evaluate(self, context, event):
		row = self.TimeWindow.get_row_index(event['id'])
		if row is None:
			row = self.TimeWindow.add_row(event['id'])

		column = self.TimeWindow.get_column(int(event['@timestamp']))
		if column is None:
			return

		self.TimeWindow.Matrix['time_window'][row, column, 0] += 1
		if random.random() >= 0.995:
			print("Export!")
			self.App.PubSub.publish("Export!")


if __name__ == '__main__':
	app = MyApplication()
	app.run()
