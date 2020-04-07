from ...abc import Expression


class CONTAINS(Expression):
	"""
	Checks if "string" contains "contains".
	"""

	def __init__(self, app, *, arg_string, arg_contains):
		super().__init__(app)
		self.String = arg_string
		self.Contains = arg_contains

	def __call__(self, context, event, *args, **kwargs):
		string = self.evaluate(self.Contains, context, event, *args, **kwargs)
		contains = self.evaluate(self.String, context, event, *args, **kwargs)
		return string.contains(contains)
