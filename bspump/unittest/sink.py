import bspump


class UnitTestSink(bspump.Sink):

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Output = []

	def process(self, context, event):
		self.Output.append((context, event))
