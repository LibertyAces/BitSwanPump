from ...abc import Expression, evaluate


class ENDSWITH(Expression):

	def __init__(self, app, *, arg_what, arg_postfix):
		super().__init__(app)
		self.What = arg_what
		self.Postfix = arg_postfix

	def __call__(self, context, event, *args, **kwargs):
		value = evaluate(self.What, context, event, *args, **kwargs)
		postfix = evaluate(self.Postfix, context, event, *args, **kwargs)
		return value.endswith(postfix)
