from bspump.analyzer import TimeWindowAnalyzer
import numpy as np

class MyTimeWindowAnalyzer(TimeWindowAnalyzer):
	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		print("ok")



	def set_time_windows(self):
		# initializing single row time windows with zeros
		self.TimeWindows = np.zeros([1, self.TimeColumnCount])

	# simple checker if event contains time related fields
	def predicate(self, event):
		if '@timestamp' not in event:
			return False

		return True

	def evaluate(self, event):
		# find the column in timewindow matrix to fit in
		column = self.get_time_column_index(event["@timestamp"])
		
		# aggregate the event into found column, 0th row
		if column is not None:
			self.TimeWindows[0, column] += 1


	async def analyze(self):
		# selecting part of matrix specified in configuration
		x = self.TimeWindows[0, :self.AnalyzeColumnCount]
		# if any of time slots is 0
		if np.any(x == 0):
			print("Alarm!")


