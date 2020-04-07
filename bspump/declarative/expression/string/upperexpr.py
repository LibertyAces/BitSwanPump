from ...abc import Expression


class UPPER(Expression):
	"""
	Transform "string" to lowercase.
	"""

	def __init__(self, app, *, arg_string):
		super().__init__(app)
		self.String = arg_string

	def __call__(self, context, event, *args, **kwargs):
		return self.evaluate(self.String, context, event, *args, **kwargs).uper()
