from ...abc import Expression


class IN(Expression):
	"""
	Checks if expression is of given list.
	"""

	def __init__(self, app, *, arg_expr, arg_is):
		super().__init__(app)
		self.Expr = arg_expr
		self.Is = arg_Is

	def __call__(self, context, event, *args, **kwargs):
		return self.evaluate(self.Is, context, event, *args, **kwargs) in self.evaluate(self.Expr, context, event, *args, **kwargs)
