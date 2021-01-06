from ...abc import Expression, evaluate


class CUT(Expression):

	Attributes = {
		"Value": ["*"],  # TODO: This ...
		"Delimiter": ["*"],  # TODO: This ...
		"Field": ["*"],  # TODO: This ...
	}

	def __init__(self, app, *, arg_what, arg_delimiter, arg_field):
		super().__init__(app)

		self.Value = arg_what

		# TODO: Delimiter must be a single character string
		self.Delimiter = arg_delimiter

		# Must be an integer
		self.Field = arg_field


	def __call__(self, context, event, *args, **kwargs):
		value = evaluate(self.Value, context, event, *args, **kwargs)
		x = value.split(self.Delimiter, self.Field + 1)
		return x[self.Field]
