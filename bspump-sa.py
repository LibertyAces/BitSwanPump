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
			UserTimeWindowAnalyzer(app, self),
			# PPrintSink(app, self)
			NullSink(app, self)
		)


class UserTimeWindowAnalyzer(TimeWindowAnalyzer):
	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, tw_format='S20', tw_dimensions=(2,2), resolution=2, clock_driven_analyze=True, id=id, config=config)


	
	def predicate(self, context, event):

		if '@timestamp' not in event:
			return False

		if event["@timestamp"] == '':
			return False

		if 'user' not in event:
			return False

		return True

	
	def evaluate(self, context, event):
		user = event["user"]
		msg = event.get('message')
		er = event.get('error')
		timestamp = int(event["@timestamp"])
		column = self.TimeWindow.get_column(timestamp)
		if user not in self.TimeWindow.RowMap:
			self.TimeWindow.add_row(user)

		if msg is not None:
			user_ind = self.TimeWindow.RowMap[user]
			self.Matrix[user_ind][column, 0] = msg

		if er is not None:
			self.Matrix[self.TimeWindow.RowMap[user]][column, 1] = er

	
	async def analyze(self):
		print("Analyzing ....")
		tw_snapshot = self.Matrix
		for i in range(0, tw_snapshot.shape[0]):
			for j in range(0, 2):
				if tw_snapshot[i][j, 1] == b'':
					print('user {} no error'.format(self.TimeWindow.RevRowMap[i]))
				else:
					print('user {} error message {}'.format(self.TimeWindow.RevRowMap[i], tw_snapshot[i][j, 0]))

			self.TimeWindow.close_row(self.TimeWindow.RevRowMap[i])
		self.TimeWindow.rebuild_rows("partial")



class GraphSessionAnalyzer(SessionAnalyzer):

	def __init__(self, app, pipeline, column_formats, column_names, id=None, config=None):
		super().__init__(app, pipeline, column_formats, column_names, clock_driven_analyze=True, id=id, config=config)

	
	
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
