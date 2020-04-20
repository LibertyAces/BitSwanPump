import datetime

from ...abc import Expression


class DATETIME_PARSE(Expression):
	"""
	Returns date/time in human readable format.
	The date is created from `datetime`, which by default is current UTC time.

	Format example: "%Y-%m-%d %H:%M:%S"
	"""

	def __init__(self, app, *, arg_value, arg_format):
		super().__init__(app)
		self.Format = arg_format
		self.Value = arg_value

	def __call__(self, context, event, *args, **kwargs):
		fmt = self.evaluate(self.Format, context, event, *args, **kwargs)
		value = self.evaluate(self.Value, context, event, *args, **kwargs)

		if fmt == 'RFC3339':
			return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
		else:
			return datetime.datetime.strptime(value, fmt)
