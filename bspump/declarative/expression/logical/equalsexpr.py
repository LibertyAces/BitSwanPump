import functools

from ..abc import Expression
from ..builder import ExpressionBuilder


class EQUALS(Expression):
	"""
	Checks if all expressions equal:

		{
			"function": "EQUALS",
			"items": [<EXPRESSION>, <EXPRESSION>...],
			"case_insensitive": false (optional)
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		self.Items = []
		for item in expression.get("items", []):
			self.Items.append(ExpressionBuilder.build(app, expression_class_registry, item))
		self.CaseInSensitive = expression.get("case_insensitive", False)

	def __call__(self, context, event, *args, **kwargs):
		if not self.CaseInSensitive:
			return functools.reduce(
				lambda x, y: x(context, event, *args, **kwargs) == y(context, event, *args, **kwargs) if isinstance(x, Expression) else x == y(context, event, *args, **kwargs),
				self.Items
			)
		else:
			return functools.reduce(
				lambda x, y: str(x(context, event, *args, **kwargs)).lower() == str(y(context, event, *args, **kwargs)).lower() if isinstance(x, Expression) else str(x).lower() == str(y(context, event, *args, **kwargs)).lower(),
				self.Items
			)
