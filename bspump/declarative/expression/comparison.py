import operator

from ..abc import SequenceExpression, Expression
from ..declerror import DeclarationError
from .value.valueexpr import VALUE
from .datastructs.itemexpr import ITEM_optimized_EVENT_VALUE


def _oper_reduce(operator, iterable, context, event, *args, **kwargs):
	it = iter(iterable)

	i = next(it)
	try:
		a = i(context, event, *args, **kwargs)
	except Exception as e:
		raise DeclarationError(original_exception=e, location=i.get_location())

	for i in it:

		try:
			b = i(context, event, *args, **kwargs)
		except Exception as e:
			raise DeclarationError(original_exception=e, location=i.get_location())

		if not operator(a, b):
			return False
		a = b

	return True


class LT(SequenceExpression):
	'''
	Operator '<'
	'''

	def __call__(self, context, event, *args, **kwargs):
		return _oper_reduce(operator.lt, self.Items, context, event, *args, **kwargs)

	def get_output_type(self):
		return bool.__name__


class LE(SequenceExpression):
	'''
	Operator '<='
	'''

	def __call__(self, context, event, *args, **kwargs):
		return _oper_reduce(operator.le, self.Items, context, event, *args, **kwargs)

	def get_output_type(self):
		return bool.__name__


class EQ(SequenceExpression):
	'''
	Operator '=='
	'''

	def __call__(self, context, event, *args, **kwargs):
		return _oper_reduce(operator.eq, self.Items, context, event, *args, **kwargs)


	def optimize(self):
		if len(self.Items) == 2 and isinstance(self.Items[1], VALUE):
			if isinstance(self.Items[0], ITEM_optimized_EVENT_VALUE):
				return EQ_optimized_EVENT_VALUE(self)
			else:
				return EQ_optimized_simple(self)
		return self

	def get_output_type(self):
		return bool.__name__


class EQ_optimized_simple(EQ):

	Attributes = {
		"A": [],  # TODO: This ...
		"B": [],  # TODO: This ...
	}

	def __init__(self, orig):
		super().__init__(orig.App, sequence=orig.Items)
		self.A = self.Items[0]
		assert isinstance(self.A, Expression)

		assert isinstance(self.Items[1], VALUE)
		self.B = self.Items[1].Value
		assert isinstance(self.B, (bool, str, int, float))

	def __call__(self, context, event, *args, **kwargs):
		return self.A(context, event, *args, **kwargs) == self.B

	def optimize(self):
		return None


class EQ_optimized_EVENT_VALUE(EQ):

	# TODO: Attributes = [...]

	def __init__(self, orig):
		super().__init__(orig.App, sequence=orig.Items)
		self.Akey = self.Items[0].Key
		self.Adefault = self.Items[0].Default

		assert isinstance(self.Items[1], VALUE)
		self.B = self.Items[1].Value
		assert isinstance(self.B, (bool, str, int, float))


	def __call__(self, context, event, *args, **kwargs):
		return event.get(self.Akey, self.Adefault) == self.B


	def optimize(self):
		return None


class NE(SequenceExpression):
	'''
	Operator '!='
	'''

	def __call__(self, context, event, *args, **kwargs):
		return _oper_reduce(operator.ne, self.Items, context, event, *args, **kwargs)

	def get_output_type(self):
		return bool.__name__


class GE(SequenceExpression):
	"""
	Operator '>='
	"""

	def __call__(self, context, event, *args, **kwargs):
		return _oper_reduce(operator.ge, self.Items, context, event, *args, **kwargs)

	def get_output_type(self):
		return bool.__name__


class GT(SequenceExpression):
	"""
	Operator '>'
	"""

	def __call__(self, context, event, *args, **kwargs):
		return _oper_reduce(operator.gt, self.Items, context, event, *args, **kwargs)

	def get_output_type(self):
		return bool.__name__


class IS(SequenceExpression):
	"""
	Operator 'is'
	"""

	def __call__(self, context, event, *args, **kwargs):
		return _oper_reduce(operator.is_, self.Items, context, event, *args, **kwargs)

	def get_output_type(self):
		return bool.__name__


class ISNOT(SequenceExpression):
	"""
	Operator 'is not'
	"""

	def __call__(self, context, event, *args, **kwargs):
		return _oper_reduce(operator.is_not, self.Items, context, event, *args, **kwargs)

	def get_output_type(self):
		return bool.__name__
