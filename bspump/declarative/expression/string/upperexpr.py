from ...abc import Expression, evaluate


class UPPER(Expression):


	def __init__(self, app, *, arg_what):
		super().__init__(app)
		self.Value = arg_what

	def __call__(self, context, event, *args, **kwargs):
		return evaluate(self.Value, context, event, *args, **kwargs).upper()
