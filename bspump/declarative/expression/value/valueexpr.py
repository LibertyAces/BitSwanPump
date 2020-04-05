from ...abc import Expression

class VALUE(Expression):
	"""
	Returns specified value:

		{
			"function": "VALUE",
			"value": "value"
		}
	"""

	def __init__(self, app, *, value):
		super().__init__(app)
		self.Value = value

	def __call__(self, context, event, *args, **kwargs):
		return self.Value
