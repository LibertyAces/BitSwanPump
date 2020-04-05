from ...abc import Expression

class STARTSWITH(Expression):
	"""
	Checks if "string" starts with "startswith"
	"""

	def __init__(self, app, *, arg_string, arg_startswith):
		super().__init__(app)
		self.String = arg_string
		self.StartsWith = arg_startswith

	def __call__(self, context, event, *args, **kwargs):
		string = self.evaluate(self.String, context, event, *args, **kwargs)
		startswith = self.evaluate(self.StartsWith, context, event, *args, **kwargs)
		return string.startswith(startswith)
