import datetime

from ...abc import Expression, evaluate


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
		self.Format = arg_format
		self.Value = arg_with if arg_with is not None else datetime.datetime.utcnow()

	def __call__(self, context, event, *args, **kwargs):
		fmt = evaluate(self.Format, context, event, *args, **kwargs)
		value = evaluate(self.Value, context, event, *args, **kwargs)
		if isinstance(value, int) or isinstance(value, float):
			value = datetime.datetime.fromtimestamp(value)
		return value.strftime(fmt)
