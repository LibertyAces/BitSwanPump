from netaddr import IPNetwork, IPAddress

from ..abc import Expression
from ..builder import ExpressionBuilder


class SUBNET(Expression):
	"""
	Checks if expression is of given subnet:

		{
			"class": "DATE",
			"subnet": <EXPRESSION>,
			"token": <EXPRESSION>
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		self.Subnet = ExpressionBuilder.build(app, expression_class_registry, expression["subnet"])
		self.Token = ExpressionBuilder.build(app, expression_class_registry, expression["token"])

	def __call__(self, context, event, *args, **kwargs):
		return IPAddress(self.Token(context, event, *args, **kwargs)) in IPNetwork(self.Subnet(context, event, *args, **kwargs))
