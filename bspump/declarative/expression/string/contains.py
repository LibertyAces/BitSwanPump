from ...abc import Expression, evaluate


class CONTAINS(Expression):


	def __init__(self, app, location, *, arg_what, arg_substring):
		super().__init__(app, location)
		self.Value = arg_what
		self.Substring = arg_substring


	def __call__(self, context, event, *args, **kwargs):
		value = evaluate(self.Value, context, event, *args, **kwargs)
		if value is None:
			return False

		substr = evaluate(self.Substring, context, event, *args, **kwargs)
		return substr in value
