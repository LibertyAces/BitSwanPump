from ...abc import Expression


class MAP(Expression):
	"""
	Checks if a given value is in the provided map in items.

	Usage:

	!MAP
	map:
		-
			- 7
			- found seven
		-
			- 8
			- found eight
	value: !ITEM EVENT potatoes
	"""

	def __init__(self, app, *, arg_map, arg_value):
		super().__init__(app)
		self.Value = arg_value
		self.Items = arg_map

	def __call__(self, context, event, *args, **kwargs):
		value = self.evaluate(self.Value, context, event, *args, **kwargs)
		for item in self.Items:
			if value == self.evaluate(item[0], context, event, *args, **kwargs):
				return self.evaluate(item[1], context, event, *args, **kwargs)
		return None
