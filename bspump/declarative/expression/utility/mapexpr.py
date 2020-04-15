from bspump.declarative.abc import Expression


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

	def __init__(self, app, *, arg_value, arg_map, arg_else=None):
		super().__init__(app)
		self.Value = arg_value
		self.Default = arg_else
		self.Map = arg_map

	def __call__(self, context, event, *args, **kwargs):
		value = self.evaluate(self.Value, context, event, *args, **kwargs)
		try:
			item = self.Map[value]
		except KeyError:
			return self.evaluate(self.Default, context, event, *args, **kwargs)
		return self.evaluate(item, context, event, *args, **kwargs)
