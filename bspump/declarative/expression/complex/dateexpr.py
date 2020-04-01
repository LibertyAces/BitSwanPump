from datetime import datetime

from ..abc import Expression
from ..builder import ExpressionBuilder


class DATE(Expression):
	"""
	Checks if expression is of given date:

		{
			"class": "DATE",
			"hours": [],
			"token": <EXPRESSION>
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		self.Hours = expression["hours"]
		self.Token = ExpressionBuilder.build(app, expression_class_registry, expression["token"])

	def __call__(self, context, event, *args, **kwargs):
		timestamp = self.Token(context, event, *args, **kwargs)
		date_time = datetime.utcfromtimestamp(timestamp)
		return date_time.hour in self.Hours
