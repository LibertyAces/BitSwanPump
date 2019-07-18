import sys
import re
import datetime
import asyncio

import numpy as np

import bspump
import bspump.file
import bspump.common
import bspump.trigger
import bspump.analyzer


###
# Download test data file from:
# http://opendata.praha.eu/dataset/parkovani_pr/resource/601ca22a-2c53-49e7-b396-26cc64cedc3d
# and save as `TSK_data_2016_2018.csv`
###

class ProgressBarProcessor(bspump.Processor):


	Spinner = [
			">   ",
			">>  ",
			">>> ",
			">>>>",
			" >>>",
			"  >>",
			"   >",
			"    ",
		]


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app=app, pipeline=pipeline, id=id, config=config)
		self.Counter = 0
		self.Time = app.Loop.time()
		self.StartTime = self.Time


	def process(self, context, event):
		self.Counter += 1
		if (self.Counter % 10000) == 0:
			t = self.Pipeline.Loop.time()
			sys.stdout.write('\r [ {} | {} events | {:0.1f} sec | {} eps ]           \r'.format(
				self.Spinner[(self.Counter // 10000) % len(self.Spinner)],
				self.nice_format(self.Counter),
				t - self.StartTime,
				self.nice_format(10000 / (t - self.Time))
			))
			sys.stdout.flush()
			self.Time = t
		return event


	@staticmethod
	def nice_format(v):
		if v > 1000000000:
			return "{:0.1f}G".format(v / 1000000000)
		if v > 1000000:
			return "{:0.1f}M".format(v / 1000000)
		if v > 1000:
			return "{:0.1f}k".format(v / 1000)
		return "{}".format(v)

###

class MyTransformator(bspump.common.MappingTransformator):

	def build(self, app):
		self.TimestampRG = re.compile(r"^([0-9]{4})\-([0-9]{2})\-([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2})$")
		return {
			'Datum_a_cas': self.timestamp,
			'Vjezd': lambda k, v: (k, int(v.replace(' ', ''))),
			'Vyjezd': lambda k, v: (k, int(v.replace(' ', ''))),
			'Obsazenost': lambda k, v: (k, int(v.replace(' ', ''))),
			'Volna_mista': lambda k, v: (k, int(v.replace(' ', ''))),
			'Kapacita': lambda k, v: (k, int(v.replace(' ', ''))),
		}

	def timestamp(self, key, value):
		rgm = self.TimestampRG.match(value)
		year, month, day, hour, minute, second = (int(x) for x in rgm.groups())
		dt = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
		return '@timestamp', dt

###

class MyTimeWindowAnalyzer(bspump.analyzer.TimeWindowAnalyzer):


	def __init__(self, app, pipeline, id=None, config=None):
		start_time=datetime.datetime(year=2016, month=1, day=1, hour=0, minute=0, second=0).timestamp()
		super().__init__(app=app, pipeline=pipeline, start_time=start_time, clock_driven=False, id=id, config=config)

		self.TimeWindow.add_row("P+R Zličín 1")
		self.TimeWindow.add_row("P+R Rajská zahrada")

		self.MaxTimestamp = 0.0


	# simple checker if event contains time related fields
	def predicate(self, context, event):
		if '@timestamp' not in event:
			return False

		return True

	def evaluate(self, context, event):
		ts = event["@timestamp"].timestamp()

		if self.MaxTimestamp < ts:
			self.MaxTimestamp = ts
			self.advance(self.MaxTimestamp)

		# find the column in timewindow matrix to fit in
		column = self.TimeWindow.get_column(ts)
		if column is None:
			return

		row = self.TimeWindow.get_row(event["Parkoviste"])
		if row is None:
			return

		self.TimeWindow.Matrix['time_window'][row, column, 0] += 1


	async def analyze(self):
		if self.TimeWindow.Matrix.shape[0] == 0:
			return

		# selecting part of matrix specified in configuration
		x = self.TimeWindow.Matrix['time_window'][:, :, 0]

		# if any of time slots is 0
		if np.any(x == 0):
			print("Alarm!")

###

class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.file.FileCSVSource(app, self, config={
					'path': './TSK_data_2016_2018.csv',
					'post': 'noop',
					'delimiter': ';',
				}).on(bspump.trigger.PubSubTrigger(app, "go!", pubsub=self.PubSub)),
			ProgressBarProcessor(app,self),
			MyTransformator(app, self),
			MyTimeWindowAnalyzer(app, self),
			bspump.common.NullSink(app, self),
		)

		self.PubSub.subscribe("bspump.pipeline.cycle_end!", self._on_cycle_end)


	async def _on_cycle_end(self, event_name, pipeline):
		await asyncio.sleep(1)

		svc = app.get_service("bspump.PumpService")
		svc.App.stop()

###

if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	pl.PubSub.publish("go!")

	app.run()

	twa = pl.locate_processor('MyTimeWindowAnalyzer')
	print("TWA:", twa)
	if twa is not None:
		print(twa.TimeWindow)
