import logging

import numpy as np

from .analyzer import Analyzer

###

L = logging.getLogger(__name__)

###


class TimeDriftAnalyzer(Analyzer):
	'''
		The analyzer, which shows how different is time of the stream from the current time.
		The output of the analyzis is a metric with average time, median time, minimum time,
		maximum time and a standart deviation.
	'''
	ConfigDefaults = {
		'analyze_period': 5 * 60,  # once per 5 minutes
		'history_size': 100,  # keep maximum 100 array members
		'sparse_count': 1,  # process every single event
	}

	def __init__(self, app, pipeline, id=None, config=None):
		# def __init__(self, app, pipeline, analyze_on_clock=False, analyze_period=None, id=None, config=None):
		super().__init__(app, pipeline, analyze_on_clock=True, id=id, config=config)

		self.History = []
		self.HistorySize = int(self.Config['history_size'])

		metrics_service = app.get_service('asab.MetricsService')

		self.DifferenceCounter = metrics_service.create_counter("timedrift.difference", tags={}, init_values={'positive': 0, 'negative': 0})
		self.Gauge = metrics_service.create_gauge(
			"timedrift",
			tags={
				'pipeline': pipeline.Id,
			},
			init_values={
				"avg": 0.0,
				"median": 0.0,
				"stddev": 0.0,
				"min": 0.0,
				"max": 0.0,
			}
		)

		self.EventCount = 0
		self.SparseCount = int(self.Config['sparse_count'])

		self.App = app


	def predicate(self, context, event):
		if "@timestamp" not in event:
			return False

		self.EventCount += 1
		if (self.EventCount % self.SparseCount) != 0:
			return False

		return True


	def get_diff(self, event_timestamp):
		'''
			Returns the time difference of current event.
		'''
		diff = self.App.time() * 1000 - event_timestamp
		return diff


	def evaluate(self, context, event):
		timestamp = event["@timestamp"]
		diff = self.get_diff(timestamp)

		if diff < 0:
			self.DifferenceCounter.add('negative', 1)
			return
		self.DifferenceCounter.add('positive', 1)

		self.History.append(diff)

		while len(self.History) > self.HistorySize:
			self.History.pop(0)


	def analyze(self):
		# in seconds
		if len(self.History) > 0:
			avg = np.mean(self.History) / 1000
			median = np.median(self.History) / 1000
			stddev = np.std(self.History) / 1000
			min_v = np.min(self.History) / 1000
			max_v = np.max(self.History) / 1000
			self.History = []
		else:
			avg = median = stddev = min_v = max_v = 0.0

		self.Gauge.set("avg", avg)
		self.Gauge.set("median", median)
		self.Gauge.set("stddev", stddev)
		self.Gauge.set("min", min_v)
		self.Gauge.set("max", max_v)
