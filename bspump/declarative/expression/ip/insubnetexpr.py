from netaddr import IPNetwork, IPAddress

from bspump.declarative.abc import Expression


class IP_INSUBNET(Expression):
	"""
	Checks if expression is of given subnet.
	"""

	def __init__(self, app, *, arg_subnet, arg_value):
		super().__init__(app)
		self.Subnet = arg_subnet
		self.Value = arg_value

	def __call__(self, context, event, *args, **kwargs):
		value = self.evaluate(self.Value, context, event, *args, **kwargs)
		subnet = self.evaluate(self.Subnet, context, event, *args, **kwargs)

		if isinstance(subnet, list):
			for element in subnet:
				if IPAddress(value) in IPNetwork(element):
					return True
		else:
			return IPAddress(value) in IPNetwork(subnet)

		return False
