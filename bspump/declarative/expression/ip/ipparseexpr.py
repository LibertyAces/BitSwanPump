from netaddr import IPAddress

import netaddr.core

from bspump.declarative.abc import Expression, evaluate


class IP_PARSE(Expression):
	"""
	Parses string, hex number or decimal number to IP address.
	"""

	Attributes = {
		"Value": ["*"],  # TODO: This ...
		"Subnet": ["*"],  # TODO: This ...
	}

	# TODO: IP.PARSE should be able to receive expressions as values natively
	def __init__(self, app, *, value=None, arg_value=None):
		super().__init__(app)
		self.Value = value if value is not None else arg_value

	def __call__(self, context, event, *args, **kwargs):
		try:
			ip = IPAddress(evaluate(self.Value, context, event, *args, **kwargs))
		except netaddr.core.AddrFormatError:
			# IP address could not be detected
			return None

		return ip.ipv6().value
