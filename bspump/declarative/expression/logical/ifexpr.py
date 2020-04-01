from ..abc import Expression
from ..builder import ExpressionBuilder


class IF(Expression):

	def __init__(self, expression: dict):
		super().__init__(expression)
		self.IfClause = ExpressionBuilder.build(expression["if"])
		self.Then = ExpressionBuilder.build(expression["then"])
		self.Else = ExpressionBuilder.build(expression["else"])

	def __call__(self, context, event, *args, **kwargs):
		if self.IfClause(context, event, *args, **kwargs):
			return self.Then(context, event, *args, **kwargs)
		else:
			return self.Else(context, event, *args, **kwargs)
