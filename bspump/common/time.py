import abc
import datetime
import logging

import pytz

import bspump

L = logging.getLogger(__name__)


class TimeZoneNormalizer(bspump.Processor):
	"""
	Normalize datetime from timezone in config to UTC
	"""

	ConfigDefaults = {
		'timezone': 'CET'
	}


	def __init__(self, app, pipeline, id=None, config=None, field_name="@timestamp"):
		"""
		:param field_name: Field name to normalize
		"""
		super().__init__(app, pipeline, id, config)
		self.FieldName = field_name
		self.TimeZoneSource = pytz.timezone(self.Config.get("timezone"))


	def normalize(self, time_stamp: datetime.datetime) -> datetime.datetime:
		"""
		Normalize time_stamp - Adds missing information about time-zone from config
		:param time_stamp: Time stamp to normalize
		:return: Normalized datetime in UTC
		"""
		local_date_time = self.TimeZoneSource.localize(time_stamp)
		return local_date_time.astimezone(pytz.utc)


	@abc.abstractmethod
	def process(self, context, event):
		"""
		Abstract method to process the event. Must be customized.

		Example:

			>>> time_stamp = event[self.FieldName]
			>>> time_stamp = self.normalize(time_stamp)
			>>> event[self.FieldName] = time_stamp
		"""
		raise NotImplemented()

