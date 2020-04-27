from netaddr import IPAddress

from bspump.declarative.abc import Expression


class IP_FORMAT(Expression):
	"""
	Parses IP address to its string representation.
	"""

	def __init__(self, app, *, value):
		super().__init__(app)
		self.Value = value

	def __call__(self, context, event, *args, **kwargs):
		ip = IPAddress(self.evaluate(self.Value, context, event, *args, **kwargs))
		return str(ip)
