import bspump.analyzer
import bspump.unittest


class TestAnalyzer(bspump.unittest.ProcessorTestCase):
	def test_analyzer(self):
		events = [
			(None, {"attribute": "value"}),
		]
		self.set_up_processor(bspump.analyzer.Analyzer)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[{"attribute": "value"}]
		)

	def test_analyzer_on_clock(self):
		events = [
			(None, {"attribute": "value"}),
		]
		self.set_up_processor(bspump.analyzer.Analyzer, processor_kwargs={
			'analyze_on_clock': True,
			'analyze_period': 60,
		})

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[{"attribute": "value"}]
		)
