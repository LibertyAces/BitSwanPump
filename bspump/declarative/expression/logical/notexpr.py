from ..abc import Expression
from ..builder import ExpressionBuilder


class NOT(Expression):
	"""
	Returns inverse value of the expression:

		{
			"function": "NOT",
			"value": <EXPRESSION>
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		self.Value = ExpressionBuilder.build(app, expression_class_registry, expression["value"])

	def __call__(self, context, event, *args, **kwargs):
		return not self.Value
