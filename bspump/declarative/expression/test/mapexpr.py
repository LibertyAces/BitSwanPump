from ...abc import Expression


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
	"""

	def __init__(self, app, *, arg_value, arg_map):
		super().__init__(app)
		self.Value = arg_value
		self.Map = arg_map

	def __call__(self, context, event, *args, **kwargs):
		value = self.evaluate(self.Value, context, event, *args, **kwargs)
		for map_key, map_value in self.Map.items():
			if value == map_key:
				return self.evaluate(map_value, context, event, *args, **kwargs)
		return None
