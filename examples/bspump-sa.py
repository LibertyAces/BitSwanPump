from bspump.file import FileCSVSource
from bspump.trigger import OpportunisticTrigger
from bspump.common import PPrintSink, NullSink
from bspump import BSPumpApplication, Pipeline, Processor
from bspump.analyzer import SessionAnalyzer, TimeWindowAnalyzer

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
			FileCSVSource(app, self, config={'path': "bspump/analyzer/var/users.csv", 'post':'noop'}).on(OpportunisticTrigger(app)),
			GraphSessionAnalyzer(app, self, column_formats=['S40', 'i8'], column_names=["user_link", "duration"]), 
			NullSink(app, self)
		)


class GraphSessionAnalyzer(SessionAnalyzer):

	def __init__(self, app, pipeline, column_formats, column_names, id=None, config=None):
		super().__init__(app, pipeline, column_formats, column_names, analyze_on_clock=True, id=id, config=config)

	
	
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
		if user_from not in self.Sessions.RowMap:
			self.Sessions.add_row(user_from, start_time)
			
		self.Matrix[self.Sessions.RowMap[user_from]]["duration"] = duration
		self.Matrix[self.Sessions.RowMap[user_from]]["user_link"] = user_to

		if user_to not in self.Sessions.RowMap:
			self.Sessions.add_row(user_to, start_time)

	
	async def analyze(self):
		graph = {}
		self.Sessions.close_row('user_1', time.time())
		sessions_snapshot = self.Matrix
		for i in range(0, sessions_snapshot.shape[0]):
			if i in self.Sessions.ClosedRows:
				continue

			user_from = self.Sessions.RevRowMap[i]
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

			self.Sessions.close_row(user_from, time.time())

		self.Sessions.rebuild_rows('full')
		L.warn("Graph is {}".format(graph))


if __name__ == '__main__':
	app = MyApplication()
	app.run()
