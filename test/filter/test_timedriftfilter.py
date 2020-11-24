from unittest.mock import patch

import bspump.filter
import bspump.unittest


class TestTimeDriftFilter(bspump.unittest.ProcessorTestCase):

	@patch("asab.metrics.metrics.Counter.flush")
	@patch("asab.application.Application.time")
	def test_time_drift_filter(self, mocked_time, mocked_flush):
		mocked_time.return_value = 100
		events = [
			(None, {"@timestamp": 40}),
			(None, {"@timestamp": 39}),
			(None, {"no": "timestamp"}),
		]

		self.set_up_processor(bspump.filter.TimeDriftFilter)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[{'@timestamp': 40}]
		)
		self.assertEqual(
			self.Pipeline.Processor.TimeDriftFilterCounter.rest_get()["Values"],
			{'event.in': 3, 'event.out': 1, 'event.drop': 1, 'timestamp.error': 1}
		)
		# TimeDriftFilter + UnitTestSink + profiler for both
		self.assertEqual(mocked_flush.call_count, 4)
