from netaddr import IPNetwork, IPAddress

from ...abc import Expression


class INSUBNET(Expression):
	"""
	Checks if expression is of given subnet.
	"""

	def __init__(self, app, *, arg_subnet, arg_value):
		super().__init__(app)
		self.Subnet = arg_subnet
		self.Value = arg_value

	def __call__(self, context, event, *args, **kwargs):
		return IPAddress(self.evaluate(self.Value, context, event, *args, **kwargs)) in IPNetwork(self.evaluate(self.Subnet, context, event, *args, **kwargs))
