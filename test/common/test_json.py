from unittest.mock import MagicMock

import bspump.unittest
import bspump.common 


class TestDictToJsonParser(bspump.unittest.ProcessorTestCase):

	def test_dict_to_json(self):
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


	def test_event_not_dict(self):
		events = [
			(None, "Not a dictionary"),
		]
		bspump.pipeline.L = MagicMock()  # turn off logging
		self.set_up_processor(bspump.common.DictToJsonParser)

		output = self.execute(events)

		self.assertTrue(self.Pipeline.is_error())
		self.assertEqual(
			[event for context, event in output],
			[]
		)
