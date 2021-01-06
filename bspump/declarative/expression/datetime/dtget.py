import datetime
from ...abc import Expression, evaluate

import pytz


class DATETIME_GET(Expression):

	Attributes = {
		"Value": ["*"],  # TODO: This ...
		"What": ["*"],  # TODO: This ...
		"Timezone": ["*"],  # TODO: This ...
	}

	def __init__(self, app, *, arg_with, arg_what, arg_timezone=None):
		super().__init__(app)

		self.Value = arg_with
		self.What = arg_what

		if arg_what in ('year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond'):
			self.Method = 1
			self.What = arg_what

		elif arg_what in ('timestamp', 'weekday', 'isoweekday'):
			self.Method = 2
			self.What = arg_what

		else:
			raise ValueError("Invalid 'what' provided: '{}'".format(arg_what))

		if arg_timezone is None:
			self.Timezone = None
		else:
			self.Timezone = pytz.timezone(arg_timezone)


	def __call__(self, context, event, *args, **kwargs):
		value = evaluate(self.Value, context, event, *args, **kwargs)
		if isinstance(value, int) or isinstance(value, float):
			value = datetime.datetime.utcfromtimestamp(value)

		# Apply the timezone
		if self.Timezone is not None:
			value = self.Timezone.localize(value)

		if self.Method == 1:
			try:
				return getattr(value, self.What)
			except AttributeError:
				return None

		elif self.Method == 2:
			func = getattr(value, self.What)
			return func()
