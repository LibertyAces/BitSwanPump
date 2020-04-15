from ...abc import Expression


class LOWER(Expression):

	def __init__(self, app, *, arg_value):
		super().__init__(app)
		self.Value = arg_value

	def __call__(self, context, event, *args, **kwargs):
		return self.evaluate(self.Value, context, event, *args, **kwargs).lower()
