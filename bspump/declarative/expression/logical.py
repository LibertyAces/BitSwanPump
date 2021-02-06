from ..abc import SequenceExpression, Expression
from ..declerror import DeclarationError
from .value.valueexpr import VALUE


class AND(SequenceExpression):
	"""
	Checks if all expressions are true, respectivelly, stop on the first False
	"""

	Attributes = {
		"Items": ['bool']
	}

	Category = "Logic"


	def __call__(self, context, event, *args, **kwargs):
		for item in self.Items:
			try:
				v = item(context, event, *args, **kwargs)
			except Exception as e:
				raise DeclarationError(original_exception=e, location=item.get_location())
			if v is None or not v:
				return False
		return True


	def get_outlet_type(self):
		return bool.__name__


	def get_items_inlet_type(self):
		return bool.__name__


class OR(SequenceExpression):
	"""
	Checks if at least one of the expressions is true
	"""

	Attributes = {
		"Items": ['bool']
	}

	Category = "Logic"


	def __call__(self, context, event, *args, **kwargs):
		for item in self.Items:
			try:
				v = item(context, event, *args, **kwargs)
			except Exception as e:
				raise DeclarationError(original_exception=e, location=item.get_location())
			if v is not None and v:
				return True
		return False


	def get_outlet_type(self):
		return bool.__name__


	def get_items_inlet_type(self):
		return bool.__name__


class NOT(Expression):
	"""
	Returns inverse value of the expression
	"""

	Attributes = {
		'What': 'bool',
	}

	Category = "Logic"


	def __init__(self, app, *, arg_what):
		super().__init__(app)
		self.What = arg_what

		if isinstance(arg_what, Expression):
			self.What = arg_what
		else:
			self.What = VALUE(app, value=arg_what)


	def __call__(self, context, event, *args, **kwargs):
		try:
			return not self.What(context, event, *args, **kwargs)
		except TypeError:
			return False


	def get_outlet_type(self):
		return bool.__name__
