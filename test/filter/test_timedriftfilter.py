from unittest.mock import patch

import bspump.filter
import bspump.unittest


class TestTimeDriftFilter(bspump.unittest.ProcessorTestCase):

	@patch("asab.application.Application.time")
	def test_attribute_filter(self, mocked_time):
		mocked_time.return_value = 100
		events = [
			(None, {"@timestamp": 40}),
		]

		self.set_up_processor(bspump.filter.TimeDriftFilter)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[{'@timestamp': 40}]
		)
