from bspump.file import FileCSVSource
from bspump.trigger import OpportunisticTrigger
from bspump.common import PPrintSink
from bspump import BSPumpApplication, Pipeline, Processor
from bspump.analyzer import SessionAnalyzer

import logging
import time
import copy

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
			PPrintSink(app, self)
		)


class GraphSessionAnalyzer(SessionAnalyzer):

	def __init__(self, app, pipeline, column_formats, column_names, id=None, config=None):
		super().__init__(app, pipeline, column_formats, column_names, id, config)
		self.AnalyzeTimer = asab.Timer(app, self._on_tick_analyze, autorestart=True)
		self.AnalyzeTimer.start(3)
	
	
	def predicate(self, event):
		if "user" not in event:
			return False

		if "duration" not in event:
			return False

		if "user_link" not in event:
			return False

		return True

	
	def evaluate(self, event):
		
		start_time = time.time()
		user_from = event["user"]
		user_to = event["user_link"]
		duration = event['duration']
		if user_from not in self.RowMap:
			self.add_session(user_from, start_time)
			
		self.Sessions[self.RowMap[user_from]]["duration"] = duration
		self.Sessions[self.RowMap[user_from]]["user_link"] = user_to

		if user_to not in self.RowMap:
			self.add_session(user_to, start_time)

	
	async def analyze(self):
		graph = {}
		self.close_session('user_1', time.time())
		sessions_snapshot = copy.copy(self.Sessions)
		for i in range(0, sessions_snapshot.shape[0]):
			if i in self.ClosedRows:
				continue

			user_from = self.RevRowMap[i]
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

			self.close_session(user_from, time.time())

		self.rebuild_sessions('full')
		L.warn("Graph is {}".format(graph))


	async def _on_tick_analyze(self):
		await self.analyze()


if __name__ == '__main__':
	app = MyApplication()
	app.run()
