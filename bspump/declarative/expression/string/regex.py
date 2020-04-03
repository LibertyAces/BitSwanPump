import re

from ..abc import Expression
from ..builder import ExpressionBuilder


class REGEX(Expression):
	"""
	Checks if "string" matches with the "regex"

		{
			"function": "REGEX",
			"string": <EXPRESSION>,
			"regex": <EXPRESSION>
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		self.String = str(ExpressionBuilder.build(app, expression_class_registry, expression["string"]))
		self.Regex = re.compile(str(ExpressionBuilder.build(app, expression_class_registry, expression["regex"])))

	def __call__(self, context, event, *args, **kwargs):
		return re.search(self.Regex, self.String)
