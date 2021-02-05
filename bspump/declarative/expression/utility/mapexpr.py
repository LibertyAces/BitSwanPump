from bspump.declarative.abc import Expression
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
		self.MapNormalized = dict()
		self.OutletType = None  # Will be determined in `initialize()`

	def set(self, key, value):
		setattr(self, key, value)

		if "Map" in key:
			self.MapNormalized[key[3:]] = value

	def initialize(self):

		for key, value in self.Map.items():

			if not isinstance(value, Expression):
				value = VALUE(self.App, value=value)

			attr_name = 'Map{}'.format(key)
			setattr(self, attr_name, value)
			if self.OutletType is None:
				self.OutletType = value.get_outlet_type()
			self.Attributes[attr_name] = self.OutletType

			self.MapNormalized[key] = value

	def __call__(self, context, event, *args, **kwargs):
		value = self.Value(context, event, *args, **kwargs)
		try:
			item = self.MapNormalized[value]
		except KeyError:
			return self.Default(context, event, *args, **kwargs)
		return item(context, event, *args, **kwargs)
