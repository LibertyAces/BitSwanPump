from ..abc import Expression
from ..builder import ExpressionBuilder


class UPDATE(Expression):
	"""
	Updates dictionary with multiple dictionaries:

		{
			"function": "UPDATE",
			"items": [<EXPRESSION>, <EXPRESSION>...]
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		self.Items = []
		self.What = expression.get("what")
		for item in expression.get("items", []):
			self.Items.append(ExpressionBuilder.build(app, expression_class_registry, item))

	def __call__(self, context, event, *args, **kwargs):
		if self.What is None:
			updated_dict = {}
		elif self.What == "event":
			updated_dict = event
		elif self.What == "context":
			updated_dict = context
		else:
			raise RuntimeError("Unknown 'what' provided: '{}'".format(this.What))
		
		for item in self.Items:
			updated_dict.update(item(context, event, *args, **kwargs))

		return updated_dict
