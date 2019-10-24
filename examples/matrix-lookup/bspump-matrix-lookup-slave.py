import logging
import bspump
import time
import bspump.common
import bspump.random
import bspump.trigger
import bspump.analyzer

from lookup import MyMatrixLookup


##

L = logging.getLogger(__name__)

##


class SlaveApplication(bspump.BSPumpApplication):
	def __init__(self):
		super().__init__()

		svc = self.get_service("bspump.PumpService")
		matrix = bspump.analyzer.SessionMatrix(self, dtype=[
			('ts_start', 'i8'), 
			('ts_end', 'i8'), 
			('time_start', 'i8'), 
			('time_end', 'i8'), 
			('channelid', 'i8'), 
			('programname', 'U30'),
			('epgid', 'i8'), 
			], id='MySessionMatrix')
		svc.add_matrix(matrix)
		
		self.Lookup = MyMatrixLookup(self, matrix_id='MySessionMatrix', id='MyLookup', config={'master_url':'http://localhost:8080', 'master_lookup_id':"MyLookup"})

		svc.add_lookup(self.Lookup)
		svc.add_pipeline(SlavePipeline(self))

		# TODO:!!! loading periodically
		

class SlavePipeline(bspump.Pipeline):
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		lb = 1567353600 - 60*60*5
		ub = 1567548000 + 60*60*5
		channel_choice = list(range(12, 1190))
		self.build(
			bspump.random.RandomSource(app, self,
				config={'number': 10, 'upper_bound': 10}
			).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=1)),
			bspump.random.RandomEnricher(app, self, config={'field':'@timestamp', 'lower_bound':lb, 'upper_bound': ub}, id="RE0"),
			bspump.random.RandomEnricher(app, self, choice=channel_choice, config={'field':'channel'}, id="RE1"),
			Enricher(app, self), 
			bspump.common.PPrintSink(app, self)
		)


class Enricher(bspump.Processor):

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		svc = app.get_service("bspump.PumpService")
		self.Lookup = svc.locate_lookup("MyLookup")

	
	def process(self, context, event):

		timestamp = event['@timestamp']
		channel = event['channel']
		st = time.time()
		# condition = (self.Lookup.Matrix.Array['channelid'] == channel) & (self.Lookup.Matrix.Array['time_start'] <= timestamp) & (self.Lookup.Matrix.Array['time_end'] > timestamp) 
		
		# program_name = self.Lookup.search(condition, 'programname')
		program_name = self.Lookup.search(event)
		end = time.time()
		event['program_name'] = program_name
		event['D'] = end-st
		return event


if __name__ == '__main__':
	app = SlaveApplication()
	app.run()
