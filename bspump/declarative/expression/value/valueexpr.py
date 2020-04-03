from ..abc import Expression


class VALUE(Expression):
	"""
	Returns specified value:

		{
			"function": "VALUE",
			"value": "value"
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		self.Value = expression["value"]

	def __call__(self, context, event, *args, **kwargs):
		return self.Value
