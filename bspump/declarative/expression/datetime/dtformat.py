import datetime

from ...abc import Expression


class DATETIME_FORMAT(Expression):
	"""
	Returns date/time in human readable format.
	The date is created from `datetime`, which by default is current UTC time.

	Format example: "%Y-%m-%d %H:%M:%S"
	"""

	def __init__(self, app, *, arg_format, arg_value=None):
		super().__init__(app)
		self.Format = arg_format
		self.Value = arg_value if arg_value is not None else datetime.datetime.utcnow()

	def __call__(self, context, event, *args, **kwargs):
		fmt = self.evaluate(self.Format, context, event, *args, **kwargs)
		value = self.evaluate(self.Value, context, event, *args, **kwargs)
		if isinstance(value, int) or isinstance(value, float):
			value = datetime.datetime.fromtimestamp(value)
		return value.strftime(fmt)
