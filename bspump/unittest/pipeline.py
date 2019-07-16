from .sink import UnitTestSink
from .source import UnitTestSource
from ..pipeline import Pipeline
from ..trigger import PubSubTrigger
from ..abc.processor import Processor
from ..application import BSPumpApplication


class UnitTestPipeline(Pipeline):

	def __init__(self, app: type(BSPumpApplication), processor: type(Processor), processor_kwargs: {} = None):
		"""
		Build Pipeline with given app and processor

		:param app:
		:param processor:
		"""
		super().__init__(app, "UnitTestPipeline")

		if processor_kwargs is None:
			processor_kwargs = {}

		self.Source = UnitTestSource(app, self).on(
			PubSubTrigger(app, "unittest.go!", self.PubSub)
		)
		self.Processor = processor(app, self, **processor_kwargs)
		self.Sink = UnitTestSink(app, self)

		self.PubSub.subscribe("bspump.pipeline.cycle_end!", self._on_finished)

		self.build(self.Source, self.Processor, self.Sink)


	def unittest_start(self):
		"""
		Start the pipeline
		"""

		self.PubSub.publish("unittest.go!")


	def _on_finished(self, event_name, pipeline):
		self.App.stop()
