from ...abc import Expression

from ..value.valueexpr import VALUE


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

		if isinstance(arg_what, Expression):
			self.What = arg_what
		else:
			self.What = VALUE(app, value=arg_what)

		if isinstance(arg_where, Expression):
			self.Where = arg_where
		else:
			self.Where = VALUE(app, value=arg_where)

		assert(self.Where.get_outlet_type() == 'list')


	def optimize(self):
		if isinstance(self.Where, VALUE):
			return IN_optimized_simple_where(self)

		return self


	def get_items_inlet_type(self):

		# Find the first usable type in the items
		for item in self.Where.Value:

			if isinstance(item, str):
				return 'str'

			elif isinstance(item, int):
				return 'int'

			elif isinstance(item, Expression):
				outlet_type = item.get_outlet_type()
				if outlet_type not in frozenset(['^']):
					return outlet_type

		raise NotImplementedError("Cannot decide on items inlet type '{}'".format(self))


	def consult_inlet_type(self, key, child):
		return self.get_items_inlet_type()


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

		self._where_value = frozenset(self.Where({}, {}))

	def optimize(self):
		# This is to prevent re-optimising the class
		return None


	def __call__(self, context, event, *args, **kwargs):
		return self.What(context, event, *args, **kwargs) in self._where_value
