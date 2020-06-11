from ...abc import Expression, evaluate


class IF(Expression):
	"""
	Checks "if" condition passes - if so, proceeds with "then" expression, otherwise with "else"
	"""

	def __init__(self, app, *, arg_test, arg_then=True, arg_else=False):
		super().__init__(app)
		self.Test = arg_test
		self.Then = arg_then
		self.Else = arg_else

	def __call__(self, context, event, *args, **kwargs):
		if evaluate(self.Test, context, event, *args, **kwargs):
			return evaluate(self.Then, context, event, *args, **kwargs)
		else:
			return evaluate(self.Else, context, event, *args, **kwargs)
