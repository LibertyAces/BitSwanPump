from ...abc import Expression


class IN(Expression):
	"""
	Checks if expression is of given list.
	"""

	Attributes = {
		"What": ["*"],  # TODO: This ...
		"Where": ["*"],  # TODO: This ...
	}

	def __init__(self, app, *, arg_what, arg_where):
		super().__init__(app)
		self.What = arg_what
		self.Where = arg_where


	def optimize(self):
		if isinstance(self.What, Expression) and isinstance(self.Where, (list, tuple, set, frozenset)):
			ok = True
			for i in self.Where:
				ok &= isinstance(i, (str, bytes, float, int, bool))
			return IN_optimized_simple_where(self)
		return self


	def __call__(self, context, event, *args, **kwargs):
		return self.What(context, event, *args, **kwargs) in self.Where(context, event, *args, **kwargs)


	def get_outlet_type(self):
		return bool.__name__


class IN_optimized_simple_where(IN):

	def __init__(self, orig):
		super().__init__(
			orig.App,
			arg_what=orig.What,
			arg_where=orig.Where
		)

		self.Where = frozenset(self.Where)


	def optimize(self):
		# This is to prevent re-optimising the class
		return None


	def __call__(self, context, event, *args, **kwargs):
		return self.What(context, event, *args, **kwargs) in self.Where
