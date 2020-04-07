import time
from datetime import datetime

from ...abc import Expression


class DATEFMT(Expression):
	"""
	Returns date/time in human readable format.
	The date is created from `datetime`, which by default is current UTC time.

	Format example: "%Y-%m-%d %H:%M:%S"
	"""

	def __init__(self, app, *, arg_format, arg_datetime=time.time()):
		super().__init__(app)
		self.Format = arg_format
		self.datetime = arg_datetime

	def __call__(self, context, event, *args, **kwargs):
		_format = self.evaluate(self.Format, context, event, *args, **kwargs)
		timestamp = self.evaluate(self.Timestamp, context, event, *args, **kwargs)
		return datetime.fromtimestamp(timestamp).strftime(_format)
