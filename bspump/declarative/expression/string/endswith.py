from ...abc import Expression


class ENDSWITH(Expression):

	def __init__(self, app, *, arg_value, arg_postfix):
		super().__init__(app)
		self.Value = arg_value
		self.Postfix = arg_postfix

	def __call__(self, context, event, *args, **kwargs):
		value = self.evaluate(self.Value, context, event, *args, **kwargs)
		postfix = self.evaluate(self.Postfix, context, event, *args, **kwargs)
		return value.endswith(postfix)
