import datetime
import pytz

from ...abc import Expression, evaluate


class DATETIME_PARSE(Expression):
	"""
	Returns date/time in human readable format.
	The date is created from `datetime`, which by default is current UTC time.

	Format example: "%Y-%m-%d %H:%M:%S"
	"""

	Attributes = {
		"Value": ["*"],  # TODO: This ...
		"Format": ["*"],  # TODO: This ...
		"Timezone": ["*"],  # TODO: This ...
	}

	def __init__(self, app, *, arg_what, arg_format, arg_flags='', arg_timezone=None):
		super().__init__(app)
		self.Format = arg_format
		self.Value = arg_what

		self.SetCurrentYear = 'Y' in arg_flags

		if arg_timezone is None:
			self.Timezone = None
		else:
			self.Timezone = pytz.timezone(arg_timezone)


	def __call__(self, context, event, *args, **kwargs):
		fmt = evaluate(self.Format, context, event, *args, **kwargs)
		value = evaluate(self.Value, context, event, *args, **kwargs)

		if isinstance(value, int) or isinstance(value, float):
			value = datetime.datetime.utcfromtimestamp(value)

		try:
			if fmt == 'RFC3339':
				dt = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
			else:
				dt = datetime.datetime.strptime(value, fmt)
		except ValueError:
			return None

		if self.SetCurrentYear:
			dt = dt.replace(year=datetime.datetime.utcnow().year)

		if self.Timezone is not None:
			dt = self.Timezone.localize(dt)
		else:
			if dt.tzinfo is None:
				# Naive datatime is considered as UTC
				dt = dt.replace(tzinfo=datetime.timezone.utc)
			else:
				# Timezone aware localtime is converted to UTC
				dt = dt.astimezone(datetime.timezone.utc)

		return dt.timestamp()
