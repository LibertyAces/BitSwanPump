from ..abc import Expression


class EVENT(Expression):
	"""
	Returns a current event:

		{
			"function": "EVENT",
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)

	def __call__(self, context, event, *args, **kwargs):
		return event
