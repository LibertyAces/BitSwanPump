from ...abc import Expression, evaluate


class LOWER(Expression):

	Attributes = {
		"Value": ["*"],  # TODO: This ...
	}

	def __init__(self, app, *, arg_what):
		super().__init__(app)
		self.Value = arg_what


	def __call__(self, context, event, *args, **kwargs):
		try:
			return evaluate(self.Value, context, event, *args, **kwargs).lower()
		except AttributeError:
			return None
