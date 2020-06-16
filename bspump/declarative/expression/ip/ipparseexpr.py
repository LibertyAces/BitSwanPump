from netaddr import IPAddress

from bspump.declarative.abc import Expression, evaluate


class IP_PARSE(Expression):
	"""
	Parses string, hex number or decimal number to IP address.
	"""

	def __init__(self, app, *, value):
		super().__init__(app)
		self.Value = value

	def __call__(self, context, event, *args, **kwargs):
		ip = IPAddress(evaluate(self.Value, context, event, *args, **kwargs))
		return ip.ipv6().value
