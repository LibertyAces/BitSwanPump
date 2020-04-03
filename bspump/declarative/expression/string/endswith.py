from ..abc import Expression
from ..builder import ExpressionBuilder


class ENDSWITH(Expression):
	"""
	Checks if "string" ends with "endswith"

		{
			"function": "ENDSWITH",
			"string": <EXPRESSION>,
			"endswith": <EXPRESSION>
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		self.String = str(ExpressionBuilder.build(app, expression_class_registry, expression["string"]))
		self.Endswith = str(ExpressionBuilder.build(app, expression_class_registry, expression["endswith"]))

	def __call__(self, context, event, *args, **kwargs):
		return self.String.endswith(self.Endswith)
