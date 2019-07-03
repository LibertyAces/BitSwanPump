from unittest.mock import MagicMock

import bspump.unittest
import bspump.common 


class TestDictToJsonParser(bspump.unittest.ProcessorTestCase):

	def test_dict_to_json_parser(self):
		events = [
			(None, {'foo': 'bar'}),
			(None, {'fizz': 'buzz'}),
			(None, {'spam': 'eggs'}),
		]

		self.set_up_processor(bspump.common.DictToJsonParser)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			['{"foo": "bar"}', '{"fizz": "buzz"}', '{"spam": "eggs"}']
		)


class TestDictToJsonParserNotDictionary(bspump.unittest.ProcessorTestCase):

	def test_event_not_dict(self):
		# pipeline = UnitTestPipeline(app, processor)

		events = [
			(None, "Not a dictionary"),
		]
		# TODO self.assertTrue(pipeline.is_error())
		# TODO self.assertIn(AssertionError(), pipeline._error)
		# TODO mock set_error

		self.set_up_processor(bspump.common.DictToJsonParser)
		svc = self.App.get_service("bspump.PumpService")
		pipeline = svc.locate("UnitTestPipeline")
		pipeline.set_error = MagicMock()
		pipeline.L = MagicMock()  # turn off logging
		# pipeline.set_error({}, 'Not a dictionary', AssertionError())

		output = self.execute(events)
		# <class 'tuple'>: ({}, 'Not a dictionary', AssertionError())

		self.assertEqual(
			[event for context, event in output],
			[]
		)

