from .sink import UnitTestSink
from .source import UnitTestSource
from ..pipeline import Pipeline
from ..trigger import PubSubTrigger
from ..abc.processor import Processor
from ..application import BSPumpApplication


class UnitTestPipeline(Pipeline):

	def __init__(self, app: type(BSPumpApplication), processor: type(Processor), *args, **kwargs):
		"""
		Build Pipeline with given app and processor

		:param processor: Processor to test - available as self.Processor
		:param args: Optional arguments for processor
		:param kwargs: Optional key-word arguments for processor
		"""
		super().__init__(app, "UnitTestPipeline")

		self.Source = UnitTestSource(app, self).on(
			PubSubTrigger(app, "Application.run!", app.PubSub)
		)
		self.Processor = processor(app, self, *args, **kwargs)
		self.Sink = UnitTestSink(app, self)

		self.PubSub.subscribe("bspump.pipeline.cycle_end!", self._on_finished)

		self.build(self.Source, self.Processor, self.Sink)


	def unittest_start(self):
		"""
		Start the pipeline
		"""
		pass


	def _on_finished(self, event_name, pipeline):
		self.App.stop()
