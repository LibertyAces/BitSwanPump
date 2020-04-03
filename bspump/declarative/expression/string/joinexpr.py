import functools

from ..abc import Expression
from ..builder import ExpressionBuilder


class JOIN(Expression):
	"""
	Joins strings in "items" using "char":

		{
			"function": "JOIN",
			"items": [<EXPRESSION>, <EXPRESSION>...],
			"char": "-" (optional)
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		self.Char = expression.get("char", "-")
		self.Items = []
		for item in expression.get("items", []):
			self.Items.append(ExpressionBuilder.build(app, expression_class_registry, item))

	def __call__(self, context, event, *args, **kwargs):
		return functools.reduce(
			lambda x, y: "{}{}{}".format(x(context, event, *args, **kwargs), self.Char, y(context, event, *args, **kwargs)) if isinstance(x, Expression) else "{}{}{}".format(x, self.Char, y(context, event, *args, **kwargs)),
			self.Items
		)
