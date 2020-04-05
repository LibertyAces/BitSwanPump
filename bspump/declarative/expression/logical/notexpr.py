from ...abc import Expression


class NOT(Expression):
	"""
	Returns inverse value of the expression
	"""

	def __init__(self, app, *, arg_value):
		super().__init__(app)
		self.Value = arg_value

	def __call__(self, context, event, *args, **kwargs):
		return not self.evaluate(self.Value, context, event, *args, **kwargs)
