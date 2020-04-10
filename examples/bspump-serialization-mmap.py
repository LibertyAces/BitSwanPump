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
		ub = int(time.time()) + 10
		lb = ub - 1000
		self.build(
			bspump.random.RandomStructuredSource(app, self,
				config={'number': 3000, 'upper_bound': 100000, 'field': 'id', 'prefix': ''}
				).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=1)),
			bspump.random.RandomEnricher(app, self, config={'field':'duration', 'lower_bound':1, 'upper_bound': 5}, id="RE0"),
			bspump.random.RandomEnricher(app, self, config={'field': '@timestamp', 'lower_bound': lb, 'upper_bound': ub}, id="RE1"),
			bspump.random.RandomEnricher(app, self, choice=['abc', 'cde', 'efg'], config={'field':'user'}, id="RE2"),
			MySessionAnalyzer(app, self, dtype=[('user', 'U10'), ('duration', 'i8')], analyze_on_clock=True, 
				config={'analyze_period': 15, 'path': 'examples/data/session.json'}), 
			# MyTimeWindowAnalyzer(app, self,  clock_driven=False, analyze_on_clock=True, 
			# 	config={'analyze_period': 20, 'path': 'examples/data/timewindow.json'}),
			NullSink(app, self)
		)


class MySessionAnalyzer(SessionAnalyzer):
	ConfigDefaults = {
		'path' : '',
	}

	def __init__(self, app, pipeline, dtype='float_', analyze_on_clock=False, id=None, config=None):
		super().__init__(app, pipeline, dtype=dtype, analyze_on_clock=analyze_on_clock, id=id, config=config)
		self.Path = self.Config['path']
		# TODO serialization

	
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
		pass
		# st = time.time()
		# data = self.Sessions.serialize()
		# with open(self.Path, 'w') as f:
		# 	json.dump(data, f)
		# end = time.time()
		# L.warning("S serialization to json took {} seconds".format(end - st))
		# st = time.time()
		# self.Sessions.deserialize(data)
		# with open(self.Path, 'r') as f:
		# 	data = json.load(f)
		# end = time.time()
		# L.warning("S deserialization from json took {} seconds".format(end - st))

	def serialize(self):
		serialized = {}
		serialized['N2IMap'] = self.N2IMap
		serialized['I2NMap'] = self.I2NMap
		serialized['ClosedRows'] = list(self.ClosedRows)
		serialized['DType'] = self.DType
		serialized['Array'] = self.Array.tolist()
		return serialized


	def deserialize(self, data):
		self.N2IMap = data['N2IMap']
		self.I2NMap = data['I2NMap']
		self.ClosedRows = set(data['ClosedRows'])

		if isinstance(data['DType'], str):
			self.DType = data['DType']
		else:
			self.DType = []
			for member in data['DType']:
				self.DType.append(tuple(member))

		array = []
		for member in data['Array']:
			array.append(tuple(member))

		self.Array = np.array(array, dtype=self.DType)



class MyTimeWindowAnalyzer(TimeWindowAnalyzer):
	ConfigDefaults = {
		'path' : '',
	}
	def __init__(self, app, pipeline, dtype='float_', clock_driven=False, analyze_on_clock=False, id=None, config=None):
		super().__init__(app, pipeline, dtype=dtype, clock_driven=clock_driven, analyze_on_clock=analyze_on_clock, id=id, config=config)
		self.Path = self.Config['path']
		# TODO serialization

	
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
		st = time.time()
		data = self.TimeWindow.serialize()
		with open(self.Path, 'w') as f:
			json.dump(data, f)
		end = time.time()
		L.warning("TW serialization to json took {} seconds".format(end - st))
		st = time.time()
		self.TimeWindow.deserialize(data)
		with open(self.Path, 'r') as f:
			data = json.load(f)
		end = time.time()
		L.warning("TW deserialization from json took {} seconds".format(end - st))


	def serialize(self):
		serialized = self.TimeWindow.serialize()
		serialized['WarmingUpCount'] = self.TimeWindow.WarmingUpCount.tolist()
		serialized['Columns'] = self.TimeWindow.Columns
		serialized['Resolution'] = self.TimeWindow.Resolution
		serialized['Start'] = self.TimeWindow.Start
		serialized['End'] = self.TimeWindow.End
		serialized['ClockDriven'] = self.TimeWindow.ClockDriven
		return serialized


	def deserialize(self, data):
		try:
			self.TimeWindow.deserialize(data)
			self.TimeWindow.WarmingUpCount = np.array(data['WarmingUpCount'])
			self.TimeWindow.Resolution = data['Resolution']
			self.TimeWindow.Columns = data['Columns']
			self.TimeWindow.ClockDriven = data['ClockDriven']
			start = data['Start']
			end = data['End']
			if self.TimeWindow.ClockDriven:
				self.TimeWindow.advance(start)
			else:
				self.TimeWindow.Start = start
				self.TimeWindow.End = end
		except TypeError as e:
			L.exception(str(e))


if __name__ == '__main__':
	app = MyApplication()
	app.run()
