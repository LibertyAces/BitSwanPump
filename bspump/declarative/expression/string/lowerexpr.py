from ...abc import Expression


class LOWER(Expression):


	def __init__(self, app, *, arg_what):
		super().__init__(app)
		self.Value = arg_what


	def __call__(self, context, event, *args, **kwargs):
		return self.evaluate(self.Value, context, event, *args, **kwargs).lower()
