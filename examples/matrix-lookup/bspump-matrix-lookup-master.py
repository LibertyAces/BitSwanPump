import logging
import numpy as np
import datetime
import time

import bspump
import bspump.analyzer
import bspump.common
import bspump.file
import bspump.trigger
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
			('channelid', 'i8'), 
			('programname', 'U30'),
			('epgid', 'i8'), 
			], id='MySessionMatrix')
		svc.add_matrix(matrix)
		lookup = MyMatrixLookup(self, matrix_id='MySessionMatrix', id='MyLookup')
		svc.add_lookup(lookup)
		pipeline = MasterPipeline(self)
		svc.add_pipeline(pipeline)



class MasterPipeline(bspump.Pipeline):
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.file.FileCSVSource(app, self,
				config={'path':'cz.o2tv.db.as.cac.live.epg.results.csv', 'delimiter':';'}
			).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=1)),
			MySessionAnalyzer(app, self, matrix_id='MySessionMatrix'),
			bspump.common.NullSink(app, self)
		)


class MySessionAnalyzer(bspump.analyzer.SessionAnalyzer):
	
	def evaluate(self, context, event):
		epgid = event['epgid']
		idx = self.Sessions.get_row_index(epgid)
		if idx is None:
			idx = self.Sessions.add_row(epgid)

		event['ts_start'] = int(datetime.datetime.strptime(event['startdate']+":00", "%Y-%m-%d %H:%M:%S%z").timestamp())
		event['ts_end'] = int(datetime.datetime.strptime(event['enddate']+":00", "%Y-%m-%d %H:%M:%S%z").timestamp())
		self.Sessions.store_event(idx, event, keys=['ts_start', 'ts_end', 'epgid', 'channelid', 'programname'])
		# print(self.Sessions.Array)



if __name__ == '__main__':
	app = MasterApplication()
	app.run()
