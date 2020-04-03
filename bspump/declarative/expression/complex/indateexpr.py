from datetime import datetime

from ..abc import Expression
from ..builder import ExpressionBuilder


class INDATE(Expression):
	"""
	Checks if expression is of given date:

		{
			"function": "INDATE",
			"hours": [],
			"value": <EXPRESSION>
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		self.Hours = expression["hours"]
		self.Value = ExpressionBuilder.build(app, expression_class_registry, expression["value"])

	def __call__(self, context, event, *args, **kwargs):
		timestamp = self.Value(context, event, *args, **kwargs)
		date_time = datetime.utcfromtimestamp(timestamp)
		return date_time.hour in self.Hours
