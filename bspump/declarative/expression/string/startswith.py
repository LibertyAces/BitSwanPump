from ...abc import Expression


class STARTSWITH(Expression):

	def __init__(self, app, *, arg_value, arg_prefix):
		super().__init__(app)
		self.Value = arg_value
		self.Prefix = arg_prefix

	def __call__(self, context, event, *args, **kwargs):
		value = self.evaluate(self.Value, context, event, *args, **kwargs)
		prefix = self.evaluate(self.Prefix, context, event, *args, **kwargs)
		return value.startswith(prefix)
