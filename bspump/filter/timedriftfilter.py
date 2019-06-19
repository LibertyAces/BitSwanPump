import logging

from ..abc.processor import Processor

##

L = logging.getLogger(__name__)

##


class TimeDriftFilter(Processor):
	"""
		TimeDriftFilter drops events, whose @timestamp (in seconds) attribute is older than current time plus configured max_time_drift (in seconds).
	"""

	ConfigDefaults = {
		"max_time_drift": 60,
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)

		self.App = app
		self.MaxTimeDrift = float(self.Config["max_time_drift"])

		metrics_service = app.get_service('asab.MetricsService')
		self.TimeDriftFilterCounter = metrics_service.create_counter(
			"timedriftfilter.status",
			tags={},
			init_values={
				'event.in': 0,
				'event.out': 0,
				'event.drop': 0,
				'timestamp.error': 0,
			}
		)

	def process(self, context, event):

		self.TimeDriftFilterCounter.add('event.in', 1)

		timestamp = event.get("@timestamp")
		if timestamp is None:
			self.TimeDriftFilterCounter.add('timestamp.error', 1)
			return None

		difference = self.App.time() - timestamp
		if difference > self.MaxTimeDrift:
			self.TimeDriftFilterCounter.add('event.drop', 1)
			return None

		self.TimeDriftFilterCounter.add('event.out', 1)
		return event
