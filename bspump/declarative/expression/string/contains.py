from ...abc import Expression
from ..value.valueexpr import VALUE


class CONTAINS(Expression):

	Attributes = {
		"Value": ["str"],
		"Substring": ["str"],
	}

	def __init__(self, app, *, arg_what, arg_substring):
		super().__init__(app)
		self.Value = arg_what

		if not isinstance(arg_substring, Expression):
			self.Substring = VALUE(app, value=arg_substring)
		else:
			self.Substring = arg_substring

	def get_outlet_type(self):
		return bool.__name__

	def consult_inlet_type(self, key, child):
		return str.__name__

	def __call__(self, context, event, *args, **kwargs):
		value = self.Value(context, event, *args, **kwargs)
		if value is None:
			return False

		substr = self.Substring(context, event, *args, **kwargs)
		return substr in value
