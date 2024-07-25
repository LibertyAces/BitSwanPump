from ...abc import Expression
from ..value.valueexpr import VALUE


class CONTEXT(Expression):
	"""
The current context.

Usage:
```
!CONTEXT
``
	"""

	Attributes = {
	}

	def __init__(self, app, *, value):
		super().__init__(app)
		assert value == ""

	def __call__(self, context, event, *args, **kwargs):
		return context


class CONTEXT_SET(Expression):

	Attributes = {
		"What": ["*"],  # TODO: This ...
	}

	def __init__(self, app, *, arg_set, arg_what=None):
		super().__init__(app)
		self.What = arg_what

		self.ArgSet = arg_set
		self.Set = None

	def set(self, key, value):
		setattr(self, key, value)

		if "Set" in key:
			self.Set[key[3:]] = value

	def initialize(self):
		if self.ArgSet is None:
			self.Set = None
		else:
			assert isinstance(self.ArgSet, dict)
			self.Set = dict()
			self._set_value_or_expression_to_attribute(self.ArgSet, self.Set, "Set")

	def _set_value_or_expression_to_attribute(self, _from, _to, name):
		for key, value in _from.items():

			# Parse value to attribute, if not expression
			if isinstance(value, Expression):
				_to[key] = value
			else:
				assert isinstance(value, (int, str, bytes, bool, tuple, list)) or value is None
				value = VALUE(self.App, value=value)
				_to[key] = value

			# Set the value to the class attribute
			attr_name = '{}{}'.format(name, key)
			setattr(self, attr_name, value)
			self.Attributes[attr_name] = value.get_outlet_type()

	def __call__(self, context, event, *args, **kwargs):
		if self.Set is not None:
			for key, value in self.Set.items():
				v = value(context, event, *args, **kwargs)
				if v is not None:
					context[key] = v

		# TODO: Optimize
		if self.What is None:
			return None

		return self.What(context, event, *args, **kwargs)
