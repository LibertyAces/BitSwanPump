from ..abc import Expression
from ..builder import ExpressionBuilder


class LIST(Expression):
	"""
	Checks if expression is of given list:

		{
			"class": "DATE",
			"list": [],
			"token": <EXPRESSION>
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		self.List = expression["list"]
		self.Token = ExpressionBuilder.build(app, expression_class_registry, expression["token"])

	def __call__(self, context, event, *args, **kwargs):
		return self.Token(context, event, *args, **kwargs) in self.List
