import bspump

from .expression import ExpressionBuilder


class DeclarativeProcessor(bspump.Processor):

	def __init__(self, app, pipeline, expression, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Expression = ExpressionBuilder.build(expression)

	def process(self, context, event):
		return self.Expression(context, event)
