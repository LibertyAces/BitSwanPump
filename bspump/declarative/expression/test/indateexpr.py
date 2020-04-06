from datetime import datetime

from ...abc import Expression


class INDATE(Expression):
	"""
	Checks if expression is of given date
	"""

	def __init__(self, app, *, arg_value, arg_hours):
		super().__init__(app)
		self.Hours = arg_hours
		self.Value = arg_value

	def __call__(self, context, event, *args, **kwargs):
		timestamp = self.evaluate(self.Value, context, event, *args, **kwargs)
		date_time = datetime.utcfromtimestamp(timestamp)
		return date_time.hour in self.evaluate(self.Hours, context, event, *args, **kwargs)
