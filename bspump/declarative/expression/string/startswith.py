from ...abc import Expression
from ..value.valueexpr import VALUE


class STARTSWITH(Expression):

	Attributes = {
		"What": ["str"],
		"Prefix": ["str"],
	}

	Category = "String"


	def __init__(self, app, *, arg_what, arg_prefix):
		super().__init__(app)

		if isinstance(arg_what, Expression):
			self.What = arg_what
		else:
			self.What = VALUE(app, value=arg_what)

		if isinstance(arg_prefix, Expression):
			self.Prefix = arg_prefix
		else:
			self.Prefix = VALUE(app, value=arg_prefix)


	def __call__(self, context, event, *args, **kwargs):
		value = self.What(context, event, *args, **kwargs)
		if value is None:
			return False

		prefix = self.Prefix(context, event, *args, **kwargs)
		return value.startswith(prefix)

