import logging
import numpy as np
import datetime
import time

import bspump
import bspump.analyzer
import bspump.common
import bspump.file
import bspump.trigger
import bspump.random
from lookup import MyMatrixLookup

##

L = logging.getLogger(__name__)

##


class MasterApplication(bspump.BSPumpApplication):
	def __init__(self):
		super().__init__(web_listen="0.0.0.0:8080")

		svc = self.get_service("bspump.PumpService")
		matrix = bspump.analyzer.SessionMatrix(self, dtype=[
			('ts_start', 'i8'), 
			('ts_end', 'i8'), 
			('time_start', 'i8'), 
			('time_end', 'i8'), 
			('channelid', 'i8'), 
			('programname', 'U30'),
			('channelname', 'U30'),
			('epgid', 'i8'), 
			], id='MySessionMatrix')
		svc.add_matrix(matrix)
		lookup = MyMatrixLookup(self, matrix_id='MySessionMatrix', on_clock_update=True, id='MyLookup')
		svc.add_lookup(lookup)
		pipeline = MasterPipeline(self)
		svc.add_pipeline(pipeline)



class MasterPipeline(bspump.Pipeline):
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		lb = 1567353600
		ub = 1567548000
		diff = ub - lb
		n = 15
		small_diff = diff / n
		ranges = []
		for i in range(0, n):
			ranges.append([int(lb + i*small_diff), int(lb + (i + 1)*small_diff)])

		self.build(
			bspump.file.FileCSVSource(app, self,
				config={'path':'cz.o2tv.db.as.cac.live.epg.results.csv', 'delimiter':';'}
			).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=1)),
			bspump.random.RandomEnricher(app, self, choice=ranges, config={'field':'range'}, id="RE0"),
			MyEnricher(app, self),
			MySessionAnalyzer(app, self, matrix_id='MySessionMatrix'),
			bspump.common.NullSink(app, self)
			# bspump.common.PPrintSink(app, self)
		)


class MyEnricher(bspump.Processor):
	def process(self, context, event):
		time_range = event.pop('range')
		event['time_start'] = time_range[0]
		event['time_end'] = time_range[1]
		return event


class MySessionAnalyzer(bspump.analyzer.SessionAnalyzer):
	
	def evaluate(self, context, event):
		epgid = event['epgid']
		idx = self.Sessions.get_row_index(epgid)
		if idx is None:
			idx = self.Sessions.add_row(epgid)

		event['ts_start'] = int(datetime.datetime.strptime(event['startdate']+":00", "%Y-%m-%d %H:%M:%S%z").timestamp())
		event['ts_end'] = int(datetime.datetime.strptime(event['enddate']+":00", "%Y-%m-%d %H:%M:%S%z").timestamp())
		self.Sessions.store_event(idx, event, keys=['ts_start', 'ts_end', 'time_start', 'time_end', 'epgid', 'channelid', 'programname', 'channelname'])



if __name__ == '__main__':
	app = MasterApplication()
	app.run()
