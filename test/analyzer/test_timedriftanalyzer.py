import bspump.analyzer
import bspump.unittest
from unittest.mock import patch


class TestTimeDriftAnalyzer(bspump.unittest.ProcessorTestCase):

	@patch("asab.application.Application.time")
	def test_time_drift_analyzer(self, mocked_time):
		mocked_time.return_value = 100
		events = [
			(None, {"@timestamp": 30000}),
			(None, {"foo": "bar"}),
		]
		self.set_up_processor(bspump.analyzer.TimeDriftAnalyzer)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[{'@timestamp': 30000}, {'foo': 'bar'}]
		)
		self.assertEqual(
			self.Pipeline.Processor.History,
			[70000]
		)
