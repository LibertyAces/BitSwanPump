from ..abc import Expression
from ..builder import ExpressionBuilder


class NOT(Expression):
	"""
	Returns inverse value of the expression:

		{
			"class": "LOWER",
			"token": <EXPRESSION>
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		self.Token = ExpressionBuilder.build(app, expression_class_registry, expression["token"])

	def __call__(self, context, event, *args, **kwargs):
		return not self.Token
