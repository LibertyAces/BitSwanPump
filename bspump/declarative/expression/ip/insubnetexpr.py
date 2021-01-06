from netaddr import IPNetwork, IPAddress

import netaddr.core

from bspump.declarative.abc import Expression, evaluate
from ..value.valueexpr import VALUE


class IP_INSUBNET(Expression):
	"""
	Checks if expression is of given subnet.
	"""

	Attributes = {
		"Value": ["*"],  # TODO: This ...
		"Subnet": ["*"],  # TODO: This ...
	}

	def __init__(self, app, *, arg_subnet, arg_what):
		super().__init__(app)
		self.Value = arg_what

		if not isinstance(arg_subnet, Expression):
			self.Subnet = VALUE(app, value=arg_subnet)
		else:
			self.Subnet = arg_subnet

	def __call__(self, context, event, *args, **kwargs):
		value = evaluate(self.Value, context, event, *args, **kwargs)
		subnet = evaluate(self.Subnet, context, event, *args, **kwargs)

		try:
			if isinstance(subnet, list):
				for element in subnet:
					if IPAddress(value) in IPNetwork(element):
						return True
			else:
				return IPAddress(value) in IPNetwork(subnet)
		except netaddr.core.AddrFormatError:
			# IP address could not be detected
			return None

		return False
