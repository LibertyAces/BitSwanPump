from ..abc import Expression
from ..builder import ExpressionBuilder


class ASSIGN(Expression):
	"""
	Assigns a value to a configured "field" in event/context:

		{
			"function": "ASSIGN",
			"target": "event/context",
			"field": "my_field",
			"value": <EXPRESSION>
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		self.Target = expression.get("target", "event")
		self.Field = expression["field"]
		self.Value = ExpressionBuilder.build(app, expression_class_registry, expression["value"])

	def __call__(self, context, event, *args, **kwargs):
		if self.Target == "event":
			event[self.Field] = self.Value(context, event, *args, **kwargs)
		elif self.Target == "context":
			context[self.Field] = self.Value(context, event, *args, **kwargs)
		return event
