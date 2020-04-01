import bspump

from .expression import ExpressionClassRegistry
from .expression import ExpressionBuilder


class DeclarativeProcessor(bspump.Processor):

	def __init__(self, app, pipeline, expression, expression_class_registry=ExpressionClassRegistry(), id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Expression = ExpressionBuilder.build(app, expression_class_registry, expression)

	def process(self, context, event):
		return self.Expression(context, event)
