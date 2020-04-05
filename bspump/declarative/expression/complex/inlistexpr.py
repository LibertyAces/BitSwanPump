from ...abc import Expression

#TODO: This ...
class INLIST(Expression):
	"""
	Checks if expression is of given list:

		{
			"function": "INLIST",
			"list": [],
			"value": <EXPRESSION>
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		self.List = expression["list"]
		self.Value = ExpressionBuilder.build(app, expression_class_registry, expression["value"])

	def __call__(self, context, event, *args, **kwargs):
		return self.Value(context, event, *args, **kwargs) in self.List
