import re

from ..abc import Expression
from ..builder import ExpressionBuilder


class REGEX(Expression):
	"""
	Checks if "string" matches with the "regex", returns True/False

		{
			"function": "REGEX",
			"regex": "<REGULAR EXPRESSION>"
			"value": <EXPRESSION>,
			"hit": <EXPRESSION> | true, // Optional, default is 'true'
			"miss": <EXPRESSION> | false, // Optional, default is 'false'
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		self.Value = ExpressionBuilder.build(app, expression_class_registry, expression["value"])
		self.Regex = re.compile(expression["regex"])
		self.Hit = expression.get("hit", True)
		self.Miss = expression.get("miss", False)
		#TODO: Regex flags

	def __call__(self, context, event, *args, **kwargs):
		value = self.Value(context, event, *args, **kwargs)
		match = re.search(self.Regex, value)
		if match is None:
			if isinstance(self.Miss, Expression):
				return self.Miss(context, event, *args, **kwargs)
			else:
				return self.Miss
		
		if isinstance(self.Hit, Expression):
			return self.Hit(context, event, *args, **kwargs)
		else:
			return self.Hit


class REGEX_PARSE(Expression):
	"""
	Checks if "string" matches with the "regex", returns True/False

		{
			"function": "REGEX_PARSE",
			"regex": "<REGULAR EXPRESSION>"
			"fields": ["<FIELD NAME>", "<FIELD NAME>", ...]
			"value": <EXPRESSION>,
			"miss": <EXPRESSION> | None, // Optional, default is 'None'
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		self.Value = ExpressionBuilder.build(app, expression_class_registry, expression["value"])
		self.Regex = re.compile(expression["regex"])
		self.Miss = expression.get("miss", None)
		self.Fields = expression.get("fields", None)
		#TODO: Regex flags

	def __call__(self, context, event, *args, **kwargs):
		value = self.Value(context, event, *args, **kwargs)
		match = re.search(self.Regex, value)
		if match is None:
			if isinstance(self.Miss, Expression):
				return self.Miss(context, event, *args, **kwargs)
			else:
				return self.Miss
		
		groups = match.groups()
		if self.Fields is None:
			return groups

		return dict(zip(self.Fields, groups))

