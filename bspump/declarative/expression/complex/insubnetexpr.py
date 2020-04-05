from netaddr import IPNetwork, IPAddress

from ...abc import Expression

#TODO: This ...
class INSUBNET(Expression):
	"""
	Checks if expression is of given subnet:

		{
			"function": "INSUBNET",
			"subnet": <EXPRESSION>,
			"value": <EXPRESSION>
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		self.Subnet = ExpressionBuilder.build(app, expression_class_registry, expression["subnet"])
		self.Value = ExpressionBuilder.build(app, expression_class_registry, expression["value"])

	def __call__(self, context, event, *args, **kwargs):
		return IPAddress(self.Value(context, event, *args, **kwargs)) in IPNetwork(self.Subnet(context, event, *args, **kwargs))
