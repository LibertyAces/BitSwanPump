from ...abc import Expression

from ..value.valueexpr import VALUE


class IF(Expression):
	"""
	Checks "if" condition passes - if so, proceeds with "then" expression, otherwise with "else"
	"""

	Attributes = {
		"Test": ["bool"],  # Test expression MUST return boolean
		"Then": ["*"],     # Then and else expression must return the same type
		"Else": ["*"],
	}

	def __init__(self, app, *, arg_test, arg_then=True, arg_else=False):
		super().__init__(app)

		if isinstance(arg_test, Expression):
			self.Test = arg_test
		else:
			self.Test = VALUE(app, value=arg_test)

		if isinstance(arg_then, Expression):
			self.Then = arg_then
		else:
			self.Then = VALUE(app, value=arg_then)

		if isinstance(arg_else, Expression):
			self.Else = arg_else
		else:
			self.Else = VALUE(app, value=arg_else)


	def __call__(self, context, event, *args, **kwargs):
		if self.Test(context, event, *args, **kwargs):
			return self.Then(context, event, *args, **kwargs)
		else:
			return self.Else(context, event, *args, **kwargs)


	def get_outlet_type(self):
		return self.Then.get_outlet_type()
