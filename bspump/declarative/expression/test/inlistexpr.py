from ...abc import Expression


class INLIST(Expression):
	"""
	Checks if expression is of given list.
	"""

	def __init__(self, app, *, arg_list, arg_value):
		super().__init__(app)
		self.List = arg_list
		self.Value = arg_value

	def __call__(self, context, event, *args, **kwargs):
		return self.evaluate(self.Value, context, event, *args, **kwargs) in self.evaluate(self.List, context, event, *args, **kwargs)
