import bspump
from bspump.trigger import OpportunisticTrigger
from bspump.common import PPrintSink, NullSink
from bspump import BSPumpApplication, Pipeline, Processor
from bspump.analyzer import SessionAnalyzer, TimeWindowAnalyzer
import bspump.random

import logging
import time

import asab


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

		self.build(
			bspump.random.RandomSource(app, self,
				config={'number': 300, 'upper_bound': 10, 'field':'user'}
				).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=.1)),
			bspump.random.RandomEnricher(app, self, config={'field':'duration', 'lower_bound':1, 'upper_bound': 5}, id="RE0"),
			bspump.random.RandomEnricher(app, self, config={'field':'user_link', 'upper_bound': 10}, id="RE1"),
			GraphSessionAnalyzer(app, self), 
			NullSink(app, self)
		)


class GraphSessionAnalyzer(SessionAnalyzer):

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, dtype=[('user_link', 'U40'), ('duration','i8')], analyze_on_clock=True, id=id, config=config)

	
	
	def predicate(self, context, event):
		if "user" not in event:
			return False

		if "duration" not in event:
			return False

		if "user_link" not in event:
			return False

		return True

	
	def evaluate(self, context, event):
		
		start_time = time.time()
		user_from = event["user"]
		user_to = event["user_link"]
		duration = event['duration']
		if user_from not in self.Sessions.N2IMap:
			self.Sessions.add_row(user_from)
			
		self.Sessions.Array[self.Sessions.N2IMap[user_from]]["duration"] = duration
		self.Sessions.Array[self.Sessions.N2IMap[user_from]]["user_link"] = user_to

		if user_to not in self.Sessions.N2IMap:
			self.Sessions.add_row(user_to)

	
	async def analyze(self):
		graph = {}
		self.Sessions.close_row('user_1')
		sessions_snapshot = self.Sessions.Array
		for i in range(0, sessions_snapshot.shape[0]):
			if i in self.Sessions.ClosedRows:
				continue

			user_from = self.Sessions.I2NMap[i]
			user_to = sessions_snapshot[i]['user_link']
			link_weight = sessions_snapshot[i]['duration']
			edge = tuple([user_to, link_weight])
			rev_edge = tuple([user_from, link_weight])

			if user_from not in graph:
				graph[user_from] = [edge]
			else:
				graph[user_from].append(edge)

			if user_to not in graph:
				graph[user_to] = [rev_edge]
			else:
				graph[user_to].append(rev_edge)

			self.Sessions.close_row(user_from)

		self.Sessions.flush()
		L.warning("Graph is {}".format(graph))


if __name__ == '__main__':
	app = MyApplication()
	app.run()
