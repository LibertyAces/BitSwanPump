import functools

from ..abc import Expression
from ..builder import ExpressionBuilder


class STARTSWITH(Expression):
	"""
	Checks if "string" starts with "startswith"

		{
			"function": "STARTSWITH",
			"string": <EXPRESSION>,
			"startswith": <EXPRESSION>
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		self.String = str(ExpressionBuilder.build(app, expression_class_registry, expression["string"]))
		self.Startswith = str(ExpressionBuilder.build(app, expression_class_registry, expression["startswith"]))

	def __call__(self, context, event, *args, **kwargs):
		return self.String.startswith(self.Startswith)
