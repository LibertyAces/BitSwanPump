import pprint

from ...abc import Expression


class DEBUG(Expression):
	"""
	Transform "string" to lowercase.
	"""

	def __init__(self, app, *, arg_expr):
		super().__init__(app)
		self.Expression = arg_expr

	def __call__(self, context, event, *args, **kwargs):
		ret = self.evaluate(self.Expression, context, event, *args, **kwargs)
		pprint.pprint(ret)
		return ret
