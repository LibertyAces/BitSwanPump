import logging
import unittest

import asab.abc.singleton
from .pipeline import UnitTestPipeline
from ..application import BSPumpApplication
from ..abc.processor import Processor


class TestCase(unittest.TestCase):
	def setUp(self) -> None:
		self.App = BSPumpApplication(args=[])


	def tearDown(self):
		asab.abc.singleton.Singleton.delete(self.App.__class__)
		self.App = None
		root_logger = logging.getLogger()
		root_logger.handlers = []


class ProcessorTestCase(TestCase):

	"""
	A class whose instances are single processor test cases.

	Test authors should subclass ProcessorTestCase for their own tests. Construction
	and deconstruction of the test's environment ('fixture') can be
	implemented by overriding the 'setUp' and 'tearDown' methods respectively.

	See :class: `unittest.TestCase` for more details

	Example of use:

	.. code-block:: python

		class MyProcessorTestCase(ProcessorTestCase)

			def test_my_processor(self):

				# setup processor for test
				self.set_up_processor(my_project.processors.MyProcessor)

				output = self.execute(
					[(None, {'foo': 'bar'})]  # Context, event
				)

				self.assertEqual(
					[event for context, event in output],
					[{'FOO': 'BAR'}]
				)

	"""


	def set_up_processor(self, processor: type(Processor), *args, **kwargs) -> None:
		"""
		Construct Pipeline from processor and appends it to PumpService

		:param processor: Processor you want to test
		:param args: Optional arguments for processor
		:param kwargs: Optional key-word arguments for processor
		"""

		svc = self.App.get_service("bspump.PumpService")

		self.Pipeline = UnitTestPipeline(self.App, processor, *args, **kwargs)
		svc.add_pipeline(self.Pipeline)


	def execute(self, input_data: []):
		"""
		Executes ProcessorTestCase

		You can define custom mocks between calling `set_up_processor` and `execute`

		:return: `input_data` processed by testing processor
		"""

		self.Pipeline.Source.Input = input_data

		# TODO catch AttributeError: 'TestIteratorSource' object has no attribute 'Pipeline'
		# Add help text - did you forget to `set_up_processor`?

		self.Pipeline.unittest_start()
		self.App.run()

		return self.Pipeline.Sink.Output
