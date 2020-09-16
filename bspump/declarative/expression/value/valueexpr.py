from ...abc import Expression


class VALUE(Expression):
	"""
	Returns specified **scalar** value
	"""

	def __init__(self, app, *, value):
		super().__init__(app)
		self.Value = value
		assert(not isinstance(self.Value, Expression))

	def __call__(self, context, event, *args, **kwargs):
		return self.Value
