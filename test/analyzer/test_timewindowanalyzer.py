import bspump.analyzer
import bspump.unittest


class TestTimeWindowAnalyzer(bspump.unittest.ProcessorTestCase):
	def test_time_window_analyzer(self):
		events = [
			(None, {"lat": 70, "lon": 10}),
			(None, {"lat": 50, "lon": 30}),
		]
		self.set_up_processor(bspump.analyzer.TimeWindowAnalyzer, clock_driven=False)  # TODO test w/ clock_driven

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[{"lat": 70, "lon": 10}, {"lat": 50, "lon": 30}]
		)

		# TODO test self.Pipeline.Processor.Matrix
