from ..abc import Expression

from ..builder import ExpressionBuilder


class FIELD(Expression):
	"""
	Obtains value of "field" from "source" (event/context):

		{
			"function": "FIELD",
			"source": <EXPRESSION>,
			"field": "field",
			"default": "None" (optional)
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		source = expression.get("source")
		if isinstance(source, dict):
			self.Source = ExpressionBuilder.build(app, expression_class_registry, source)
		else:
			if source is None:
				self.Source = "event"
			else:
				self.Source = source
		self.Field = expression["field"]
		self.Default = expression.get("default")

	def __call__(self, context, event, *args, **kwargs):
		if self.Source == "event":
			return event.get(self.Field, self.Default)
		elif self.Source == "context":
			return context.get(self.Field, self.Default)
		elif isinstance(self.Source, Expression):
			expression_value = self.Source(context, event, *args, **kwargs)
			if isinstance(expression_value, dict):
				return expression_value.get(self.Field, self.Default)
			else:
				return expression_value[self.Field]

		return None
