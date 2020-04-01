from ..abc import Expression
from ..builder import ExpressionBuilder


class IF(Expression):
	"""
	Checks "if" condition passes - if so, proceeds with "then" expression, otherwise with "else":

		{
			"class": "IF",
			"if": <EXPRESSION>,
			"then": <EXPRESSION>,
			"else": <EXPRESSION>
		}

	TODO: IF should be more "tenary" operator
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		self.IfClause = ExpressionBuilder.build(app, expression_class_registry, expression["if"])
		self.Then = ExpressionBuilder.build(app, expression_class_registry, expression["then"])
		self.Else = ExpressionBuilder.build(app, expression_class_registry, expression["else"])

	def __call__(self, context, event, *args, **kwargs):
		if self.IfClause(context, event, *args, **kwargs):
			return self.Then(context, event, *args, **kwargs)
		else:
			return self.Else(context, event, *args, **kwargs)
