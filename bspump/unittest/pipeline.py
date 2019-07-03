from .sink import UnitTestSink
from .source import UnitTestSource
from ..pipeline import Pipeline
from ..trigger import RunOnceTrigger


class UnitTestPipeline(Pipeline):

	def __init__(self, app, processor):
		super().__init__(app, "UnitTestPipeline")

		self.Source = UnitTestSource(app, self).on(
			RunOnceTrigger(app)
		)
		self.Processor = processor(app, self)
		self.Sink = UnitTestSink(app, self)

		self.build(self.Source, self.Processor, self.Sink)
