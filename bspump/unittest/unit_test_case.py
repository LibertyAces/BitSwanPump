import unittest

from .pipeline import UnitTestPipeline
from ..application import BSPumpApplication


class ProcessorTestCase(unittest.TestCase):

	'''
	This is processor test case
	'''

	def setUp(self) -> None:
		self.App = BSPumpApplication()

	def set_up_processor(self, processor):

		svc = self.App.get_service("bspump.PumpService")

		self.Pipeline = UnitTestPipeline(self.App, processor)
		svc.add_pipeline(self.Pipeline)

	def execute(self, input_data):
		'''
		This is universal and become part of bspump.unitest.ProcessorTestCase module
		'''

		self.Pipeline.Source.Input = input_data

		self.App.run()

		return self.Pipeline.Sink.Output

