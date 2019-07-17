from unittest.mock import MagicMock

import bspump.unittest
import bspump.common


class TestStringToBytesParser(bspump.unittest.ProcessorTestCase):

	def test_string_to_bytes_parser(self):
		events = {
			(None, 'some string'),
			(None, 'another string'),
			(None, 'last string'),
		}

		self.set_up_processor(bspump.common.StringToBytesParser)

		output = self.execute(
			events
		)

		self.assertEqual(
			sorted([event for context, event in output]),
			[b"another string", b"last string", b"some string"]
		)


	def test_event_not_string(self):
		events = [
			(None, b"Not a string"),
		]
		self.set_up_processor(bspump.common.StringToBytesParser)

		output = self.execute(events)

		self.assertTrue(self.Pipeline.is_error())
		self.assertEqual(
			[event for context, event in output],
			[]
		)


class TestBytesToStringParser(bspump.unittest.ProcessorTestCase):

	def test_bytes_to_string_parser(self):
		events = {
			(None, b'some bytes'),
			(None, b'another bytes'),
			(None, b'last bytes'),
		}

		self.set_up_processor(bspump.common.BytesToStringParser)

		output = self.execute(
			events
		)

		self.assertListEqual(
			sorted([event for context, event in output]),
			["another bytes", "last bytes", "some bytes"]
		)


	def test_event_not_bytes(self):
		events = [
			(None, "Not a bytes"),
		]
		self.set_up_processor(bspump.common.BytesToStringParser)

		bspump.pipeline.L = MagicMock()  # turn off logging

		output = self.execute(events)

		self.assertTrue(self.Pipeline.is_error())
		self.assertEqual(
			[event for context, event in output],
			[]
		)
