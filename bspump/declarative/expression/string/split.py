import logging

from ...abc import Expression
from ..value.valueexpr import VALUE

###

L = logging.getLogger(__name__)

###


class SPLIT(Expression):

	Attributes = {
		"Value": ["str"],
		"Separator": ["str"],
	}

	Category = "String"


	def __init__(self, app, *, arg_value, arg_separator):
		super().__init__(app)

		if isinstance(arg_value, Expression):
			self.Value = arg_value
		else:
			self.Value = VALUE(app, value=arg_value)

		if isinstance(arg_separator, Expression):
			self.Separator = arg_separator
		else:
			self.Separator = VALUE(app, value=arg_separator)


	def __call__(self, context, event, *args, **kwargs):
		value = self.Value(context, event, *args, **kwargs)
		separator = self.Separator(context, event, *args, **kwargs)

		try:
			return value.split(separator)
		except AttributeError:
			return None
