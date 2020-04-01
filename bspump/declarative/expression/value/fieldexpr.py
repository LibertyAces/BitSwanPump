from ..abc import Expression


class FIELD(Expression):
	"""
	Obtains value of "field" from "source" (event/context):

		{
			"class": "FIELD",
			"source": "event/context",
			"field": "field",
			"default": "None" (optional)
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		self.Source = expression.get("source", "event")
		self.Field = expression["field"]
		self.Default = expression.get("default")

	def __call__(self, context, event, *args, **kwargs):
		field = {"context": context, "event": event}
		field_dimensions = self.Source.split(".")
		for field_dimension in field_dimensions:
			field = field.get(field_dimension)
		field = field.get(self.Field)

		if field is None:
			return self.Default
		else:
			return field
