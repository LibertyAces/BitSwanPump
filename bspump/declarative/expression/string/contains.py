from ...abc import Expression, evaluate


class CONTAINS(Expression):


	def __init__(self, app, *, arg_what, arg_substring):
		super().__init__(app)
		self.Value = arg_what
		self.Substring = arg_substring


	def __call__(self, context, event, *args, **kwargs):
		value = evaluate(self.Value, context, event, *args, **kwargs)
		substr = evaluate(self.Substring, context, event, *args, **kwargs)
		return value.contains(substr)
