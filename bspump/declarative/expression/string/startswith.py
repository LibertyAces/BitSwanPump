from ...abc import Expression, evaluate
from ..value.valueexpr import VALUE


class STARTSWITH(Expression):

	Attributes = {
		"Value": ["*"],  # TODO: This ...
		"Prefix": ["*"],  # TODO: This ...
	}

	def __init__(self, app, *, arg_what, arg_prefix):
		super().__init__(app)
		self.Value = arg_what

		if not isinstance(arg_prefix, Expression):
			self.Prefix = VALUE(app, value=arg_prefix)
		else:
			self.Prefix = arg_prefix

	def __call__(self, context, event, *args, **kwargs):
		value = evaluate(self.Value, context, event, *args, **kwargs)
		if value is None:
			return False

		prefix = evaluate(self.Prefix, context, event, *args, **kwargs)
		return value.startswith(prefix)
