import time
from datetime import datetime

from ...abc import Expression


class DATE(Expression):
	"""
	Returns date in human readable "format".
	The date is created from "timestamp", which by default is current UTC timestamp.

	Format example: "%Y-%m-%d %H:%M:%S"
	"""

	def __init__(self, app, *, arg_format, arg_timestamp=time.time()):
		super().__init__(app)
		self.Format = arg_format
		self.Timestamp = arg_timestamp

	def __call__(self, context, event, *args, **kwargs):
		_format = self.evaluate(self.Format, context, event, *args, **kwargs)
		timestamp = self.evaluate(self.Timestamp, context, event, *args, **kwargs)
		return datetime.fromtimestamp(timestamp).strftime(_format)
