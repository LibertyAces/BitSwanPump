from ..abc import Expression
from ..builder import ExpressionBuilder


class NOT(Expression):

	def __init__(self, expression: dict):
		super().__init__(expression)
		self.Value = ExpressionBuilder.build(expression["value"])

	def __call__(self, context, event, *args, **kwargs):
		return not self.Value
