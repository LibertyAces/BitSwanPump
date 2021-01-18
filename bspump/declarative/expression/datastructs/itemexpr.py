from ...abc import Expression, evaluate

from ..value.eventexpr import EVENT
from ..value.eventexpr import KWARGS
from ..value.eventexpr import ARG
from ..value.valueexpr import VALUE
from ..utility.context import CONTEXT


class ITEM(Expression):
	"""
Get the item from a dictionary.

There are two forms:

1) Mapping form

!ITEM
with: !EVENT
item: foo
default: 0

2) Scalar form

!ITEM EVENT potatoes

Scalar form has some limitations (e.g no default value) but it is more compact
	"""

	Attributes = {
		"With": ["*"],  # TODO: This ...
		"Item": ["*"],  # TODO: This ...
		"Default": ["*"],  # TODO: This ...
	}

	def __init__(self, app, *, arg_with=None, arg_item=None, arg_default=None, value=None):
		super().__init__(app)

		self.OutletType = '^'  # Inlet type is to be set based on the parent advice

		if value is not None:
			# Scalar value provided
			with_, item = value.split(' ', 2)

			with_ = with_.upper()
			if with_ == 'EVENT':
				self.With = EVENT(app, value='')
			elif with_ == 'CONTEXT':
				self.With = CONTEXT(app, value='')
			elif with_ == 'KWARGS':
				self.With = KWARGS(app, value='')
			elif with_ == 'ARG':
				self.With = ARG(app, value='')
			else:
				raise RuntimeError("Invalid item argument '{}' - must be EVENT, CONTEXT, KWARGS, ARG", format(with_))

			self.Item = VALUE(app, value=item)
			self.Default = VALUE(app, value=None)

		else:
			self.With = arg_with
			self.Item = VALUE(app, value=arg_item)

			if isinstance(arg_default, Expression):
				self.Default = arg_default
			else:
				self.Default = VALUE(app, value=arg_default)


	def optimize(self):

		if isinstance(self.With, EVENT) and isinstance(self.Item, VALUE):
			return ITEM_optimized_EVENT_VALUE(self)

		elif isinstance(self.With, CONTEXT) and isinstance(self.Item, VALUE):
			if "." in self.Item.Value:
				return ITEM_optimized_CONTEXT_VALUE_NESTED(self)
			else:
				return ITEM_optimized_CONTEXT_VALUE(self)
		return None


	def __call__(self, context, event, *args, **kwargs):
		with_dict = evaluate(self.With, context, event, *args, **kwargs)
		item = evaluate(self.Item, context, event, *args, **kwargs)

		try:
			return with_dict[item]

		except KeyError:
			if self.Default is None:
				return None
			return evaluate(self.Default, context, event, *args, **kwargs)

		except IndexError:
			if self.Default is None:
				return None
			return evaluate(self.Default, context, event, *args, **kwargs)


class ITEM_optimized_EVENT_VALUE(ITEM):

	def __init__(self, orig):
		super().__init__(orig.App)

		self.With = orig.With
		self.Item = orig.Item
		self.Default = orig.Default

		if self.Default is None:
			self.DefaultValue = None
		elif isinstance(self.Default, VALUE):
			self.DefaultValue = self.Default(None, None)
		else:
			raise NotImplementedError("Default: {}".format(self.Default))

		self.Key = self.Item.Value
		self.OutletType = orig.OutletType

	def get_outlet_type(self):
		return self.OutletType

	def set_outlet_type(self, outlet_type):
		self.OutletType = outlet_type

	def optimize(self):
		# This is to prevent re-optimising the class
		return None

	def __call__(self, context, event, *args, **kwargs):
		return event.get(self.Key, self.DefaultValue)


class ITEM_optimized_CONTEXT_VALUE(ITEM):

	def __init__(self, orig):
		super().__init__(orig.App)

		self.With = orig.With
		self.Item = orig.Item
		self.Default = orig.Default

		self.Key = self.Item.Value

		if self.Default is None:
			self.DefaultValue = None
		elif isinstance(self.Default, VALUE):
			self.DefaultValue = self.Default(None, None)
		else:
			raise NotImplementedError("Default: {}".format(self.Default))

		self.OutletType = orig.OutletType

	def get_outlet_type(self):
		return self.OutletType

	def set_outlet_type(self, outlet_type):
		self.OutletType = outlet_type

	def optimize(self):
		# This is to prevent re-optimising the class
		return None

	def __call__(self, context, event, *args, **kwargs):
		return context.get(self.Key, self.Default)


class ITEM_optimized_CONTEXT_VALUE_NESTED(ITEM):

	def __init__(self, orig):
		super().__init__(orig.App)

		self.With = orig.With
		self.Item = orig.Item
		self.Default = orig.Default

		if self.Default is None:
			self.DefaultValue = None
		elif isinstance(self.Default, VALUE):
			self.DefaultValue = self.Default(None, None)
		else:
			raise NotImplementedError("Default: {}".format(self.Default))

		# TODO: Replace with JSON pointer path
		self.KeyList = self.Item.Value.split('.')

		self.OutletType = orig.OutletType

	def get_outlet_type(self):
		return self.OutletType

	def set_outlet_type(self, outlet_type):
		self.OutletType = outlet_type

	def optimize(self):
		# This is to prevent re-optimising the class
		return None

	def __call__(self, context, event, *args, **kwargs):
		value = context
		try:
			for key in self.KeyList:
				if isinstance(value, list):
					value = value[int(key)]
				else:
					value = value[key]
		except (TypeError, KeyError, IndexError):
			return self.DefaultValue

		return value
