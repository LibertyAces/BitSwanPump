from unittest.mock import MagicMock

import bspump.unittest
import bspump.common


class TestDictToJsonBytesParser(bspump.unittest.ProcessorTestCase):

	def test_dict_to_json_bytes(self):
		events = [
			(None, {'foo': 'bar'}),
			(None, {'fizz': 'buzz'}),
			(None, {'spam': 'eggs'}),
		]

		self.set_up_processor(bspump.common.DictToJsonBytesParser)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[b'{"foo": "bar"}', b'{"fizz": "buzz"}', b'{"spam": "eggs"}']
		)


	def test_event_not_dict(self):
		events = [
			(None, "Not a dictionary"),
		]
		bspump.pipeline.L = MagicMock()  # turn off logging
		self.set_up_processor(bspump.common.DictToJsonBytesParser)

		output = self.execute(events)

		self.assertTrue(self.Pipeline.is_error())
		self.assertEqual(
			[event for context, event in output],
			[]
		)


class TestJsonBytesToDictParser(bspump.unittest.ProcessorTestCase):

	def test_json_bytes_to_dict(self):
		events = {
			(None, b'{"key": "1"}'),
			(None, b'{"key": "2"}'),
			(None, b'{"key": "3"}'),
		}

		self.set_up_processor(bspump.common.JsonBytesToDictParser)

		output = self.execute(
			events
		)

		self.assertListEqual(
			sorted([event for context, event in output], key=lambda d: int(d["key"])),
			[{"key": "1"}, {"key": "2"}, {"key": "3"}]
		)


	def test_event_not_byte(self):
		events = [
			(None, "Not a byte"),
		]
		self.set_up_processor(bspump.common.JsonBytesToDictParser)

		output = self.execute(events)

		self.assertTrue(self.Pipeline.is_error())
		self.assertEqual(
			[event for context, event in output],
			[]
		)
