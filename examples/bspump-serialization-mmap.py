import bspump
from bspump.trigger import OpportunisticTrigger
from bspump.common import PPrintSink, NullSink
from bspump import BSPumpApplication, Pipeline, Processor
from bspump.analyzer import SessionAnalyzer, TimeWindowAnalyzer, GeoAnalyzer
import bspump.random

import logging
import time

import asab
import json
import numpy as np

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
			bspump.random.RandomGeneratorSource(app, self,
				config={'number': 30, 'upper_bound': 1000, 'field': 'id', 'prefix': ''}
				).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=1)),
			bspump.random.RandomEnricher(app, self, config={'field':'duration', 'lower_bound':1, 'upper_bound': 5}, id="RE0"),
			bspump.random.RandomEnricher(app, self, config={'field': '@timestamp', 'lower_bound': lb, 'upper_bound': ub}, id="RE1"),
			bspump.random.RandomEnricher(app, self, choice=['abc', 'cde', 'efg'], config={'field':'user'}, id="RE2"),
			bspump.random.RandomEnricher(app, self, choice=[{'lat': 50, 'lon': 14}, {'lat':52, 'lon': 13}, {'lat': 48, 'lon': 17}], config={'field':'L'}, id="RE3"),
			# MySessionAnalyzer(app, self, dtype=[('user', 'U10'), ('duration', 'i8')], analyze_on_clock=True, persistent=True,
			# 	config={'analyze_period': 5, 'path':'examples/mmap/sessions'}), 
			# MyTimeWindowAnalyzer(app, self, columns=10, resolution=2, clock_driven=True, analyze_on_clock=True, persistent=True,
			# 	config={'analyze_period': 5, 'path': 'examples/mmap/timewindow'}),
			MyGeoAnalyzer(app, self, resolution=10, analyze_on_clock=True, persistent=True,
				config={'analyze_period': 5, 'path': 'examples/mmap/geo'}),
			NullSink(app, self)
		)


class MySessionAnalyzer(SessionAnalyzer):	
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
		self.Sessions.close_row('2')
		self.Sessions.close_row('8')



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
		self.TimeWindow.close_row('2')
		self.TimeWindow.close_row('5')
		self.TimeWindow.close_rows(['4', '2', '6'])


class MyGeoAnalyzer(GeoAnalyzer):
	def evaluate(self, context, event):
		lat = event['L']['lat']
		lon = event['L']['lon']
		x,y = self.GeoMatrix.project_equirectangular(lat, lon)
		self.GeoMatrix.Array[x, y] += 1

	def analyze(self):
		coordinates = np.where(self.GeoMatrix.Array != 0)
		xx = coordinates[0]
		yy = coordinates[1]
		for i in range(len(xx)):
			x = xx[i]
			y = yy[i]
			print(self.GeoMatrix.inverse_equirectangular(x, y), self.GeoMatrix.Array[x, y])

if __name__ == '__main__':
	app = MyApplication()
	app.run()
