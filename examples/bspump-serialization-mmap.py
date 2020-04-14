import bspump
from bspump.trigger import OpportunisticTrigger
from bspump.common import PPrintSink, NullSink
from bspump import BSPumpApplication, Pipeline, Processor
from bspump.analyzer import SessionAnalyzer, TimeWindowAnalyzer
import bspump.random

import logging
import time

import asab
import json

##
L = logging.getLogger(__name__)
##


class MyApplication(BSPumpApplication):
	def __init__(self):
		super().__init__()
		svc = self.get_service("bspump.PumpService")
		svc.add_pipeline(MyPipeline(self))
		
		

class MyPipeline(Pipeline):
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		ub = int(time.time()) + 2
		lb = ub - 22
		self.build(
			bspump.random.RandomStructuredSource(app, self,
				config={'number': 30, 'upper_bound': 7, 'field': 'id', 'prefix': ''}
				).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=1)),
			bspump.random.RandomEnricher(app, self, config={'field':'duration', 'lower_bound':1, 'upper_bound': 5}, id="RE0"),
			bspump.random.RandomEnricher(app, self, config={'field': '@timestamp', 'lower_bound': lb, 'upper_bound': ub}, id="RE1"),
			bspump.random.RandomEnricher(app, self, choice=['abc', 'cde', 'efg'], config={'field':'user'}, id="RE2"),
			# MySessionAnalyzer(app, self, dtype=[('user', 'U10'), ('duration', 'i8')], analyze_on_clock=True, persistent=True,
			# 	config={'analyze_period': 15, 'path':'examples/mmap/sessions'}), 
			MyTimeWindowAnalyzer(app, self, columns=10, resolution=2, clock_driven=True, analyze_on_clock=True, persistent=True,
				config={'analyze_period': 10, 'path': 'examples/mmap/timewindow'}),
			NullSink(app, self)
		)


class MySessionAnalyzer(SessionAnalyzer):
	def __init__(self, app, pipeline, dtype='float_', analyze_on_clock=False, persistent=False, id=None, config=None):
		super().__init__(app, pipeline, dtype=dtype, analyze_on_clock=analyze_on_clock, persistent=persistent, id=id, config=config)

	
	def evaluate(self, context, event):
		id_ = event["id"]
		user = event["user"]
		duration = event['duration']
		row = self.Sessions.get_row_index(id_)
		if row is None:
			row = self.Sessions.add_row(id_)
		self.Sessions.Array[row]["duration"] = duration
		self.Sessions.Array[row]["user"] = user

	
	def analyze(self):
		print("BEFORE")
		print("???", self.Sessions.Array)
		print("!!", self.Sessions.Index.serialize())
		print("77&7", self.Sessions.ClosedRows.serialize())

		# self.Sessions.close_row(2)
		# self.Sessions.close_row(8)
		# print("AFTER (0)")
		# print("???", self.Sessions.Array)
		# print("!!", self.Sessions.Index.serialize())
		# print("77&7", self.Sessions.ClosedRows.serialize())
		
		# self.Sessions.close_rows([4, 2, 7])
		# print("AFTER(1)")
		# print("???", self.Sessions.Array)
		# print("!!", self.Sessions.Index.serialize())
		# print("77&7", self.Sessions.ClosedRows.serialize())
		


class MyTimeWindowAnalyzer(TimeWindowAnalyzer):	
	def evaluate(self, context, event):
		id_ = event["id"]
		timestamp = event['@timestamp']
		row = self.TimeWindow.get_row_index(id_)
		if row is None:
			row = self.TimeWindow.add_row(id_)
			
		column = self.TimeWindow.get_column(timestamp)
		if column is None:
			return

		self.TimeWindow.Array[row, column] += 1 

	
	def analyze(self):
		print("BEFORE")
		print("???", self.TimeWindow.Array)
		print("!!", self.TimeWindow.Index.serialize())
		print("77&7", self.TimeWindow.ClosedRows.serialize())
		print("$$$$$$", self.TimeWindow.TimeConfig.TC)
		print("^^^^^^", self.TimeWindow.WarmingUpCount.WUC)
		# self.TimeWindow.close_row(2)
		# self.TimeWindow.close_row(5)
		# print("AFTER (0)")
		# print("???", self.TimeWindow.Array)
		# print("!!", self.TimeWindow.Index.serialize())
		# print("77&7", self.TimeWindow.ClosedRows.serialize())
		
		# self.TimeWindow.close_rows([4, 2, 6])
		# print("AFTER(1)")
		# print("???", self.TimeWindow.Array)
		# print("!!", self.TimeWindow.Index.serialize())
		# print("77&7", self.TimeWindow.ClosedRows.serialize())


if __name__ == '__main__':
	app = MyApplication()
	app.run()
