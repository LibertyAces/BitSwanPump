import bspump.analyzer
import bspump.unittest
import mongoquery


class CustomSmallLatchAnalyzer(bspump.analyzer.LatchAnalyzer):
	ConfigDefaults = {
		'latch_max_size': 2,
	}


class CustomInfiniteLatchAnalyzer(bspump.analyzer.LatchAnalyzer):
	ConfigDefaults = {
		'latch_max_size': 0,
	}


class TestLatch(bspump.unittest.ProcessorTestCase):
	def test_analyzer(self):
		events = [
			(None, {"foo": "bar"}),
			(None, {"fizz": "buzz"}),
		]
		self.set_up_processor(CustomSmallLatchAnalyzer)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[{"foo": "bar"}, {"fizz": "buzz"}]
		)
		self.assertEqual(len(self.Pipeline.Processor.Latch), 2)

	def test_analyzer_query_false(self):
		events = [
			(None, {"foo": "bar"}),
			(None, {"fizz": "buzz"}),
		]
		self.set_up_processor(CustomSmallLatchAnalyzer, query=False)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[{"foo": "bar"}, {"fizz": "buzz"}]
		)
		self.assertEqual(len(self.Pipeline.Processor.Latch), 0)

	def test_infinite_analyzer_query_false(self):
		events = [
			(None, {"foo": "bar"}),
			(None, {"fizz": "buzz"}),
		]
		self.set_up_processor(CustomInfiniteLatchAnalyzer, query=False)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[{"foo": "bar"}, {"fizz": "buzz"}]
		)
		self.assertEqual(len(self.Pipeline.Processor.Latch), 0)
		self.assertIsNone(self.Pipeline.Processor.Latch.maxlen)

	def test_analyzer_with_mongo_query(self):
		events = [
			(None, {"foo": "bar"}),
			(None, {"fizz": "buzz"}),
		]
		self.set_up_processor(CustomSmallLatchAnalyzer, query={"foo": "bar"})

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[{"foo": "bar"}, {"fizz": "buzz"}]
		)
		self.assertEqual(list(self.Pipeline.Processor.Latch), [{"foo": "bar"}])

	def test_analyzer_with_mongo_query_inclusive(self):
		events = [
			(None, {"foo": "bar"}),
			(None, {"fizz": "buzz"}),
		]
		self.set_up_processor(CustomSmallLatchAnalyzer, query={"foo": "bar"}, inclusive=True)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[{"foo": "bar"}, {"fizz": "buzz"}]
		)
		self.assertEqual(list(self.Pipeline.Processor.Latch), [{"fizz": "buzz"}])

	def test_analyzer_with_invalid_query(self):
		with self.assertRaises(mongoquery.QueryError):
			self.set_up_processor(bspump.analyzer.LatchAnalyzer, query={"$foo": 2})
