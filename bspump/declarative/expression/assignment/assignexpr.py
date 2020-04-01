from ..abc import Expression
from ..builder import ExpressionBuilder


class ASSIGN(Expression):

	def __init__(self, app, expression: dict):
		super().__init__(app, expression)
		self.Target = expression.get("target", "event")
		self.Field = expression["field"]
		self.Token = ExpressionBuilder.build(app, expression["token"])

	def __call__(self, context, event, *args, **kwargs):
		if self.Target == "event":
			event[self.Field] = self.Token(context, event, *args, **kwargs)
		elif self.Target == "context":
			context[self.Field] = self.Token(context, event, *args, **kwargs)
		return event
