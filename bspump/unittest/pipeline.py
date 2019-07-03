from .sink import UnitTestSink
from .source import UnitTestSource
from ..pipeline import Pipeline
from ..trigger import PubSubTrigger


class UnitTestPipeline(Pipeline):


	def __init__(self, app, processor):
		super().__init__(app, "UnitTestPipeline")

		self.Source = UnitTestSource(app, self).on(
			PubSubTrigger(app, "unittest.go!", self.PubSub)
		)
		self.Processor = processor(app, self)
		self.Sink = UnitTestSink(app, self)

		self.PubSub.subscribe("bspump.pipeline.cycle_end!", self._on_finished)

		self.build(self.Source, self.Processor, self.Sink)


	def unittest_start(self):
		# Start the pipeline
		self.PubSub.publish("unittest.go!")


	def _on_finished(self, event_name, pipeline):
		self.App.stop()
