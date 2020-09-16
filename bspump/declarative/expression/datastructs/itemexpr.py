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
				self.With = EVENT(app=app, value='')
			elif with_ == 'CONTEXT':
				self.With = CONTEXT(app=app, value='')
			elif with_ == 'KWARGS':
				self.With = KWARGS(app=app, value='')
			elif with_ == 'ARG':
				self.With = ARG(app=app, value='')
			else:
				raise RuntimeError("Invalid item argument '{}' - must be EVENT, CONTEXT, KWARGS, ARG", format(with_))

			self.Item = VALUE(app=app, value=item)
			self.Default = None

		else:
			self.With = arg_with
			self.Item = arg_item
			self.Default = arg_default

	def __call__(self, context, event, *args, **kwargs):
		with_dict = evaluate(self.With, context, event, *args, **kwargs)
		item = evaluate(self.Item, context, event, *args, **kwargs)

		try:
			if '.' in item:
				value = with_dict
				for i in item.split('.'):
					try:
						if isinstance(value, list):
							value = value[int(i)]
						else:
							value = value[i]
					except TypeError:
						value = None
			else:
				value = with_dict[item]
		except KeyError:
			if self.Default is None:
				return None
			return evaluate(self.Default, context, event, *args, **kwargs)
		except IndexError:
			if self.Default is None:
				return None
			return evaluate(self.Default, context, event, *args, **kwargs)

		return value
