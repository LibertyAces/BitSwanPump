from netaddr import IPAddress

from bspump.declarative.abc import Expression


class IP(Expression):
	"""
	Parses string, hex number or decimal number to IP address.
	"""

	def __init__(self, app, *, value):
		super().__init__(app)
		self.Value = value

	def __call__(self, context, event, *args, **kwargs):
		ip = IPAddress(self.evaluate(self.Value, context, event, *args, **kwargs))
		return ip.value
