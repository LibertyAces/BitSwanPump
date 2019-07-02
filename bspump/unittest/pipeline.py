import bspump
import bspump.trigger

from .sink import UnitTestSink
from .source import UnitTestSource


class UnitTestPipeline(bspump.Pipeline):

	def __init__(self, app, processor):
		super().__init__(app, "UnitTestPipeline")

		self.Source = UnitTestSource(app, self).on(
			bspump.trigger.RunOnceTrigger(app)
		)
		self.Processor = processor(app, self)
		self.Sink = UnitTestSink(app, self)

		self.build(self.Source, self.Processor, self.Sink)
