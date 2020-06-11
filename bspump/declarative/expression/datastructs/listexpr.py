from ...abc import Expression, evaluate


class LIST(Expression):

	def __init__(self, app, *, arg_with=None, arg_append=None):
		super().__init__(app)

		self.With = arg_with

		if arg_append is not None:
			assert(isinstance(arg_append, list))
		self.Append = arg_append



	def __call__(self, context, event, *args, **kwargs):
		if self.With is None:
			with_list = dict()
		else:
			with_list = evaluate(self.With, context, event, *args, **kwargs)
			if not isinstance(with_list, list):
				with_list = list()

		if self.Append is not None:
			for value in self.Append:
				with_list.append(
					evaluate(value, context, event, *args, **kwargs)
				)

		return with_list
