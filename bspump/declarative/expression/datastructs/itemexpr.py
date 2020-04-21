from ...abc import Expression

from ..value.eventexpr import EVENT, CONTEXT, KWARGS, ARG
from ..value.valueexpr import VALUE


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

	def __call__(self, context, event, *args, **kwargs):
		with_dict = self.evaluate(self.With, context, event, *args, **kwargs)
		item = self.evaluate(self.Item, context, event, *args, **kwargs)

		try:
			value = with_dict[item]
		except KeyError:
			if self.Default is None:
				return None
			return self.evaluate(self.Default, context, event, *args, **kwargs)
		except IndexError:
			if self.Default is None:
				return None
			return self.evaluate(self.Default, context, event, *args, **kwargs)

		return value
