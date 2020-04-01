from ..abc import Expression
from ..builder import ExpressionBuilder


class UPDATE(Expression):
	"""
	Updates dictionary with multiple dictionaries:

		{
			"class": "UPDATE",
			"items": [<EXPRESSION>, <EXPRESSION>...]
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		self.Items = []
		for item in expression.get("items", []):
			self.Items.append(ExpressionBuilder.build(app, expression_class_registry, item))

	def __call__(self, context, event, *args, **kwargs):
		updated_dict = {}
		for item in self.Items:
			updated_dict.update(item(context, event, *args, **kwargs))
		return updated_dict
