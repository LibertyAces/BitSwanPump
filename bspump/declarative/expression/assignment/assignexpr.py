from ..abc import Expression
from ..builder import ExpressionBuilder


class ASSIGN(Expression):
	"""
	Assigns a token to a configured "field" in event/context:

		{
			"class": "ASSIGN",
			"target": "event/context",
			"field": "my_field",
			"token": <EXPRESSION>
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		self.Target = expression.get("target", "event")
		self.Field = expression["field"]
		self.Token = ExpressionBuilder.build(app, expression_class_registry, expression["token"])

	def __call__(self, context, event, *args, **kwargs):
		if self.Target == "event":
			event[self.Field] = self.Token(context, event, *args, **kwargs)
		elif self.Target == "context":
			context[self.Field] = self.Token(context, event, *args, **kwargs)
		return event
