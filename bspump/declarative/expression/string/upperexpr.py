from ...abc import Expression, evaluate


class UPPER(Expression):


	def __init__(self, app, location, *, arg_what):
		super().__init__(app, location)
		self.Value = arg_what

	def __call__(self, context, event, *args, **kwargs):
		return evaluate(self.Value, context, event, *args, **kwargs).upper()
