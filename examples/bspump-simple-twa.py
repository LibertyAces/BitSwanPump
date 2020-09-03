import datetime

import numpy as np

import bspump
import bspump.file
import bspump.common
import bspump.random
import bspump.trigger
import bspump.analyzer


class MyTimeWindowAnalyzer(bspump.analyzer.TimeWindowAnalyzer):
	"""
	Simple Time Window analyzer examples, that prints alarms
	if number of logins exceeds or is equal to 2.
	"""

	ConfigDefaults = {
		"analyze_period": 2,  # every 2 seconds
	}

	def __init__(self, app, pipeline, id=None, config=None):
		start_time=datetime.datetime(year=2020, month=8, day=31, hour=8, minute=0, second=0).timestamp()
		super().__init__(
			columns=20,
			resolution=30,
			dtype="i2",
			analyze_on_clock=True,
			app=app, pipeline=pipeline, start_time=start_time, clock_driven=False,
			id=id, config=config)
		self.MaxTimestamp = 0.0

	def predicate(self, context, event):
		if '@timestamp' not in event or 'user' not in event:
			return False
		return True

	def evaluate(self, context, event):
		timestamp = event["@timestamp"]

		if self.MaxTimestamp < timestamp:
			self.MaxTimestamp = timestamp
			self.TimeWindow.advance(self.MaxTimestamp)

		# find the column in timewindow matrix to fit in
		column = self.TimeWindow.get_column(timestamp)
		if column is None:
			return

		row = self.TimeWindow.get_row_index(event["user"])
		if row is None:
			row = self.TimeWindow.add_row(event["user"])

		self.TimeWindow.Array[row, column] += 1
		print(">>> Item added to row: {}, column: {}, sum: {} ({})".format(
			row,
			column,
			self.TimeWindow.Array[row, column],
			str(event)
		))

	def analyze(self):
		if self.TimeWindow.Array.shape[0] == 0:
			return

		# selecting part of matrix specified in configuration
		x = self.TimeWindow.Array[:, :]

		for row in range(0, len(x)):
			for column in range(0, len(x[row])):
				if x[row][column] > 2:
					print("More than two logins at row '{}' and column '{}'.".format(row, column))


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.random.RandomSource(app, self, choice=[
				{"@timestamp": 1598866568, "user": "Adam"},
				{"@timestamp": 1598866585, "user": "Andrew"},
				{"@timestamp": 1598866590, "user": "Adam"},
			], config={"number": 3}).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=10)),
			MyTimeWindowAnalyzer(app, self),
			bspump.common.NullSink(app, self),
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()
