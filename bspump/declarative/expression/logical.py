from ..abc import SequenceExpression, Expression
from ..declerror import DeclarationError


class AND(SequenceExpression):
	"""
	Checks if all expressions are true, respectivelly, stop on the first False
	"""

	def __call__(self, context, event, *args, **kwargs):
		for item in self.Items:
			try:
				v = item(context, event, *args, **kwargs)
			except Exception as e:
				raise DeclarationError(original_exception=e, location=item.get_location())
			if v is None or not v:
				return False
		return True


	def get_type(self):
		return bool.__name__


class OR(SequenceExpression):
	"""
	Checks if at least one of the expressions is true
	"""

	def __call__(self, context, event, *args, **kwargs):
		for item in self.Items:
			try:
				v = item(context, event, *args, **kwargs)
			except Exception as e:
				raise DeclarationError(original_exception=e, location=item.get_location())
			if v is not None and v:
				return True
		return False


	def get_type(self):
		return bool.__name__


class NOT(Expression):
	"""
	Returns inverse value of the expression
	"""

	def __init__(self, app, *, arg_what):
		super().__init__(app)
		self.Value = arg_what


	def __call__(self, context, event, *args, **kwargs):
		try:
			return not self.Value(context, event, *args, **kwargs)
		except TypeError:
			# Incompatible types included
			return None


	def get_type(self):
		return bool.__name__
