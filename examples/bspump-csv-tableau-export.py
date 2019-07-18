from bspump import BSPumpApplication, Pipeline
import bspump.trigger
import bspump.random
import bspump.common
import bspump.analyzer
import bspump.file
from bspump.file.filetableausink import FileTableauSink
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
		svc.add_pipeline(SecondaryPipelineCSV(self))
		svc.add_pipeline(SecondaryPipelineTableau(self))
		svc.add_pipeline(PrimaryPipeline(self))

		

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
				).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=1)),
			bspump.random.RandomEnricher(app, self, config={'field':'@timestamp', 'lower_bound':lb, 'upper_bound': ub}, id="RE0"),
			bspump.random.RandomEnricher(app, self, config={'field':'fraction', 'lower_bound':lb_0, 'upper_bound': ub_0}, id="RE1"),
			MySessionAnalyzer(app, self, column_formats, column_names, analyze_on_clock=True, config={'analyze_period': 1}),
			bspump.common.NullSink(app, self)
		)


class SecondaryPipelineCSV(Pipeline):
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.common.InternalSource(app, self),
			bspump.file.FileCSVSink(app, self, config={'path':'abc.csv'})
		)

class SecondaryPipelineTableau(Pipeline):
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.common.InternalSource(app, self),
			FileTableauSink(app, self,config={'path':'abc.tde'})
		)


class MySessionAnalyzer(bspump.analyzer.SessionAnalyzer):
	Translate = {
		'a':'abc',
		'b':'bcd',
		'c':'cdef',
	}

	def __init__(self, app, pipeline, column_formats, column_names, analyze_on_clock, id=None, config=None):
		super().__init__(app, pipeline, column_formats, column_names, analyze_on_clock=analyze_on_clock, id=id, config=config)
		svc = app.get_service("bspump.PumpService")
		self.CSVInternalSource = svc.locate("SecondaryPipelineCSV.*InternalSource")
		self.TableauInternalSource = svc.locate("SecondaryPipelineTableau.*InternalSource")


	def evaluate(self, context, event):
		row = self.Sessions.get_row(event['id'])
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


	async def analyze(self):
		print("export!")
		await self.export_to_csv(self.CSVInternalSource)
		await self.export_to_tableau(self.TableauInternalSource)



if __name__ == '__main__':
	app = MyApplication()
	app.run()
