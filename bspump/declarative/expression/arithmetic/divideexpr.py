import functools

from ..abc import Expression
from ..builder import ExpressionBuilder


class DIVIDE(Expression):

	def __init__(self, app, expression: dict):
		super().__init__(app, expression)
		self.Items = []
		for item in expression.get("items", []):
			self.Items.append(ExpressionBuilder.build(app, item))

	def __call__(self, context, event, *args, **kwargs):
		return functools.reduce(
			lambda x, y: x(context, event, *args, **kwargs) / y(context, event, *args, **kwargs) if isinstance(x, Expression) else x / y(context, event, *args, **kwargs),
			self.Items
		)
