from netaddr import IPAddress

from bspump.declarative.abc import Expression


class IP_FORMAT(Expression):
	"""
	Parses IP address to its string representation.
	"""

	def __init__(self, app, *, arg_value, arg_format="ipv6"):
		super().__init__(app)
		self.Value = arg_value
		self.Format = arg_format

	def __call__(self, context, event, *args, **kwargs):
		ip = IPAddress(self.evaluate(self.Value, context, event, *args, **kwargs))

		if self.Format == "ipv6":
			return str(ip.ipv6())
		elif self.Format == "ipv4":
			return str(ip.ipv4())
		else:
			return str(ip)
