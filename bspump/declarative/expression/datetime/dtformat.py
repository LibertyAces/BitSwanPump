import datetime
import pytz

import asab

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

	Category = "Date/Time"


	def __init__(self, app, *, arg_format, arg_with=None, arg_timezone=None):
		super().__init__(app)
		self.Value = arg_with if arg_with is not None else datetime.datetime.utcnow()
		if not isinstance(self.Value, Expression):
			self.Value = VALUE(app, value=self.Value)

		if not isinstance(arg_format, Expression):
			self.Format = VALUE(app, value=arg_format)
		else:
			self.Format = arg_format

		if arg_timezone is None:
			timezone_from_config = asab.Config["declarations"]["local_timezone"]

			if len(timezone_from_config) == 0:
				self.Timezone = None

			else:
				self.Timezone = pytz.timezone(timezone_from_config)

		else:
			self.Timezone = pytz.timezone(arg_timezone)

	def __call__(self, context, event, *args, **kwargs):
		fmt = self.Format(context, event, *args, **kwargs)
		value = self.Value(context, event, *args, **kwargs)
		if isinstance(value, int) or isinstance(value, float):
			value = datetime.datetime.fromtimestamp(value, tz=self.Timezone)
		return value.strftime(fmt)
