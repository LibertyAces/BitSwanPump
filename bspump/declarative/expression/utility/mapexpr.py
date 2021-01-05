from bspump.declarative.abc import Expression, evaluate
from ..value.valueexpr import VALUE


class MAP(Expression):
	"""
	Checks if a given value is in the provided map in items.

	Usage:

	!MAP
	value: !ITEM EVENT potatoes
	map:
		7: only seven
		20: twenty
		12: twelve
		10: enough
	else:
		nothing found
	"""

	Attributes = {
		"Value": ["*"],  # TODO: This ...
		"Default": ["*"],  # TODO: This ...
		"Map": ["*"],  # TODO: This ...
	}

	def __init__(self, app, *, arg_what, arg_in, arg_else=None):
		super().__init__(app)
		self.Value = arg_what
		self.Default = arg_else

		if not isinstance(arg_else, Expression):
			self.Default = VALUE(app, value=arg_else)
		else:
			self.Default = arg_else

		self.Map = arg_in


	def __call__(self, context, event, *args, **kwargs):
		value = evaluate(self.Value, context, event, *args, **kwargs)
		try:
			item = self.Map[value]
		except KeyError:
			return evaluate(self.Default, context, event, *args, **kwargs)
		return evaluate(item, context, event, *args, **kwargs)
