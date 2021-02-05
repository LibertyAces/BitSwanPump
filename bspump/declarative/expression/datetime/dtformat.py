import datetime

from ...abc import Expression
from ..value.valueexpr import VALUE


class DATETIME_FORMAT(Expression):
	"""
	Returns date/time in human readable format.
	The date is created from `datetime`, which by default is current UTC time.

	Format example: "%Y-%m-%d %H:%M:%S"
	"""

	Attributes = {
		"Format": ["*"],  # TODO: This ...
		"Value": ["*"],  # TODO: This ...
	}

	def __init__(self, app, *, arg_format, arg_with=None):
		super().__init__(app)
		self.Value = arg_with if arg_with is not None else datetime.datetime.utcnow()
		if not isinstance(self.Value, Expression):
			self.Value = VALUE(app, value=self.Value)

		if not isinstance(arg_format, Expression):
			self.Format = VALUE(app, value=arg_format)
		else:
			self.Format = arg_format

	def __call__(self, context, event, *args, **kwargs):
		fmt = self.Format(context, event, *args, **kwargs)
		value = self.Value(context, event, *args, **kwargs)
		if isinstance(value, int) or isinstance(value, float):
			value = datetime.datetime.fromtimestamp(value)
		return value.strftime(fmt)
