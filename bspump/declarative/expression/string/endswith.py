from ...abc import Expression


class ENDSWITH(Expression):
	"""
	Checks if "string" ends with "endswith".
	"""

	def __init__(self, app, *, arg_string, arg_endswith):
		super().__init__(app)
		self.String = arg_string
		self.EndsWith = arg_endswith

	def __call__(self, context, event, *args, **kwargs):
		string = self.evaluate(self.String, context, event, *args, **kwargs)
		endswith = self.evaluate(self.EndsWith, context, event, *args, **kwargs)
		return string.endswith(endswith)
