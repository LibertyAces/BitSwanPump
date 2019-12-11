import abc
import datetime
import logging

import pytz

import bspump

L = logging.getLogger(__name__)


class TimeZoneNormalizer(bspump.Processor):
	"""
	Normalizes datetime from local timezone (e.g. in config) to UTC, which is preferred internal datetime form
	"""

	ConfigDefaults = {
		'timezone': 'CET'
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		self.TimeZoneSource = pytz.timezone(self.Config.get("timezone"))


	def normalize(self, local_time: datetime.datetime) -> datetime.datetime:
		"""
		If `local_time` doesn't contain a time zone (e.g. it is naive), the timezone will be added from config

		:param local_time: Local time to normalize
		:return: Normalized `local_time` in UTC
		"""
		if not local_time.tzinfo:
			local_time = self.TimeZoneSource.localize(local_time)
		return local_time.astimezone(pytz.utc)


	@abc.abstractmethod
	def process(self, context, event):
		"""
		Abstract method to process the event. Must be customized.

		Example:

			>>> native_time = event["@timestamp"]
			>>> local_time = self.normalize(native_time)
			>>> event["@timestamp"] = local_time
		"""
		raise NotImplementedError()
