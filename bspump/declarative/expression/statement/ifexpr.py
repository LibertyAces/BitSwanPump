from ...abc import Expression


class IF(Expression):
	"""
	Checks "if" condition passes - if so, proceeds with "then" expression, otherwise with "else"
	"""

	def __init__(self, app, *, arg_is, arg_then, arg_else):
		super().__init__(app)
		self.Test = arg_is
		self.Then = arg_then
		self.Else = arg_else

	def __call__(self, context, event, *args, **kwargs):
		if self.evaluate(self.Test, context, event, *args, **kwargs):
			return self.evaluate(self.Then, context, event, *args, **kwargs)
		else:
			return self.evaluate(self.Else, context, event, *args, **kwargs)
