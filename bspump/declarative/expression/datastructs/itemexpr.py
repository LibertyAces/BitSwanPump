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

	def __init__(self, app, *, arg_with=None, arg_item=None, arg_default=None, value=None):
		super().__init__(app)

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
			self.Default = None

		else:
			self.With = arg_with
			self.Item = arg_item
			self.Default = arg_default


	def optimize(self):
		if isinstance(self.With, EVENT) and isinstance(self.Item, VALUE):
			return ITEM_optimized_EVENT_VALUE(
				self,
				arg_with=self.With,
				arg_item=self.Item,
				arg_default=self.Default
			)
		return self


	def __call__(self, context, event, *args, **kwargs):
		with_dict = evaluate(self.With, context, event, *args, **kwargs)
		item = evaluate(self.Item, context, event, *args, **kwargs)

		try:

			if isinstance(self.With, CONTEXT):
				return self.evaluate_CONTEXT(with_dict, item)

			return with_dict[item]

		except KeyError:
			if self.Default is None:
				return None
			return evaluate(self.Default, context, event, *args, **kwargs)

		except IndexError:
			if self.Default is None:
				return None
			return evaluate(self.Default, context, event, *args, **kwargs)


	def evaluate_CONTEXT(self, with_dict, item):

		if '.' in item:
			value = with_dict
			for i in item.split('.'):
				try:
					if isinstance(value, list):
						value = value[int(i)]
					else:
						value = value[i]
				except KeyError as e:
					raise e
				except TypeError:
					return None
			return value

		else:
			return with_dict[item]


class ITEM_optimized_EVENT_VALUE(ITEM):

	def __init__(self, orig, *, arg_with, arg_item, arg_default):
		super().__init__(orig.App)

		self.With = arg_with
		self.Item = arg_item
		if arg_default is None:
			self.Default = arg_default
		else:
			# TODO: Default must be statically evaluated
			raise NotImplementedError("")

		self.Key = self.Item.Value


	def __call__(self, context, event, *args, **kwargs):
		return event.get(self.Key, self.Default)
