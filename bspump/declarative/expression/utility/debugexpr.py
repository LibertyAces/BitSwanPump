import pprint
import logging

from ...abc import Expression

###

L = logging.getLogger("bspump.declarative.DEBUG")

###


class DEBUG(Expression):
	"""
	Transform "string" to lowercase.
	"""

	def __init__(self, app, *, arg_what):
		super().__init__(app)
		self.What = arg_what

	def __call__(self, context, event, *args, **kwargs):
		ret = self.evaluate(self.What, context, event, *args, **kwargs)
		L.warning(pprint.pformat(ret))
		return ret
