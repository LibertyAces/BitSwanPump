import sys
from unittest.mock import patch, call

import bspump.common
import bspump.unittest


class TestPrintSink(bspump.unittest.ProcessorTestCase):

	@patch('builtins.print')
	def test_print_sink(self, mocked_print):
		events = [
			(None, "Please, print this to me"),
		]

		self.set_up_processor(bspump.common.PrintSink)

		output = self.execute(
			events
		)
		self.assertEqual(
			mocked_print.mock_calls[1],
			call("Please, print this to me", file=sys.stdout)
		)

		self.assertEqual(
			[event for context, event in output],
			[]
		)


class TestPPrintSink(bspump.unittest.ProcessorTestCase):

	@patch('pprint.PrettyPrinter.pprint')
	def test_pprint_sink(self, mocked_print):
		event = {"list": ["a", "b"], "dict": {"a": "b"}}
		events = [
			(None, event),
		]

		self.set_up_processor(bspump.common.PPrintSink)

		output = self.execute(
			events
		)

		mocked_print.assert_called_with(event)

		self.assertEqual(
			[event for context, event in output],
			[]
		)


class TestPrintProcessor(bspump.unittest.ProcessorTestCase):

	@patch('builtins.print')
	def test_print_processor(self, mocked_print):
		event = "Please, print this to me"
		events = [
			(None, event),
		]

		self.set_up_processor(bspump.common.PrintProcessor)

		output = self.execute(
			events
		)
		self.assertEqual(
			mocked_print.mock_calls[1],
			call("Please, print this to me", file=sys.stdout)
		)

		self.assertEqual(
			[event for context, event in output],
			[event]
		)


class TestPPrintProcessor(bspump.unittest.ProcessorTestCase):

	@patch('pprint.PrettyPrinter.pprint')
	def test_pprint_processor(self, mocked_print):
		event = {"list": ["a", "b"], "dict": {"a": "b"}}
		events = [
			(None, event),
		]

		self.set_up_processor(bspump.common.PPrintProcessor)

		output = self.execute(
			events
		)

		mocked_print.assert_called_with(event)

		self.assertEqual(
			[event for context, event in output],
			[event]
		)


class TestPrintContextProcessor(bspump.unittest.ProcessorTestCase):

	@patch('builtins.print')
	def test_print_context_processor(self, mocked_print):
		context = {"context": "dict"}
		events = [
			(context, None),
		]

		self.set_up_processor(bspump.common.PrintContextProcessor)

		output = self.execute(
			events
		)
		self.assertEqual(
			mocked_print.mock_calls[1],
			call(context, file=sys.stdout)
		)

		self.assertEqual(
			[event for context, event in output],
			[]
		)


class TestPPrintContextProcessor(bspump.unittest.ProcessorTestCase):

	@patch('pprint.PrettyPrinter.pprint')
	def test_pprint_context_processor(self, mocked_print):
		context = {"context": "dict"}
		events = [
			(context, None),
		]

		self.set_up_processor(bspump.common.PPrintContextProcessor)

		output = self.execute(
			events
		)

		mocked_print.assert_called_with(context)

		self.assertEqual(
			[event for context, event in output],
			[]
		)
