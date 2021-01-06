from ...abc import Expression, evaluate
from ..value.valueexpr import VALUE


class CONTAINS(Expression):

	Attributes = {
		"Value": ["*"],  # TODO: This ...
		"Substring": ["*"],  # TODO: This ...
	}

	def __init__(self, app, *, arg_what, arg_substring):
		super().__init__(app)
		self.Value = arg_what

		if not isinstance(arg_substring, Expression):
			self.Substring = VALUE(app, value=arg_substring)
		else:
			self.Substring = arg_substring

	def __call__(self, context, event, *args, **kwargs):
		value = evaluate(self.Value, context, event, *args, **kwargs)
		if value is None:
			return False

		substr = evaluate(self.Substring, context, event, *args, **kwargs)
		return substr in value
