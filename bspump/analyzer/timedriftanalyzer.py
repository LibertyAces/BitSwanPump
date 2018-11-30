import time
import logging
import asyncio

import numpy as np

import asab

from .analyzer import Analyzer

###

L = logging.getLogger(__name__)

###

class TimeDriftAnalyzer(Analyzer):

	ConfigDefaults = {
		'stats_period' : 5*60, # once per 5 minutes
		'history_size' : 100, # keep maximum 100 array members
		'sparse_count' : 1, # process every single event
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		
		self.History = []
		self.HistorySize = self.Config['history_size']

		metrics_service = app.get_service('asab.MetricsService')
		self.Gauge = metrics_service.create_gauge("timedrift",
			tags = {
				'pipeline': pipeline.Id,
			},
			init_values = {
				"avg": 0.0,
				"median" : 0.0,
				"stddev": 0.0,
				"min" : 0.0,
				"max" : 0.0,
			}
		)
		
		self.EventCount = 0
		self.SparseCount = int(self.Config['sparse_count'])

		self.Timer = asab.Timer(app, self.on_tick, autorestart=True)
		self.Timer.start(self.Config['stats_period'])

		self.App = app


	async def on_tick(self):
		await self.analyze()


	def predicate(self, event):
		if "@timestamp" not in event:
			return False

		self.EventCount += 1
		if (self.EventCount % self.SparseCount) != 0:
			return False

		return True


	def get_diff(self, event_timestamp):
		diff = self.App.time()*1000 - event_timestamp
		return diff


	def evaluate(self, event):
		timestamp = event["@timestamp"]
		diff = self.get_diff(timestamp)

		if diff < 0:
			L.warning("Negative timestamp")
			return

		self.History.append(diff)

		while len(self.History) > self.HistorySize:
			self.History.pop(0)


	async def analyze(self):
		# in seconds
		if len(self.History) > 0:
			self.Gauge.set("avg", np.mean(self.History)/1000)
			self.Gauge.set("median", np.median(self.History)/1000)
			self.Gauge.set("stddev", np.std(self.History)/1000)
			self.Gauge.set("min", np.min(self.History)/1000)
			self.Gauge.set("max", np.max(self.History)/1000)

			self.History = []
