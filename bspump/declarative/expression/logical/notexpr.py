from ..abc import Expression
from ..builder import ExpressionBuilder


class NOT(Expression):

	def __init__(self, app, expression: dict):
		super().__init__(app, expression)
		self.Value = ExpressionBuilder.build(app, expression["value"])

	def __call__(self, context, event, *args, **kwargs):
		return not self.Value
