import pytz
import datetime
import bspump.common
import bspump.unittest


class CustomTimeNormalizer(bspump.common.TimeZoneNormalizer):

	def process(self, context, event):
		native_time = event["@timestamp"]
		local_time = self.normalize(native_time)
		return local_time


class TestCustomTimeZoneNormalizer(bspump.unittest.ProcessorTestCase):

	def test_timezone_normalizer(self):
		events = [(None, {  # native time
			"@timestamp": datetime.datetime(2000, 12, 30, 23, 59, 59, 59)
		})]

		self.set_up_processor(CustomTimeNormalizer)

		output = self.execute(
			events
		)

		self.assertEqual(  # local time represented in UTC
			[event for context, event in output],
			[datetime.datetime(2000, 12, 30, 22, 59, 59, 59, tzinfo=pytz.UTC)]
		)


class TestAbstractTimeZoneNormalizer(bspump.unittest.ProcessorTestCase):

	def test_abstract_timezone_normalizer(self):
		with self.assertRaises(TypeError):
			self.set_up_processor(bspump.common.TimeZoneNormalizer)
