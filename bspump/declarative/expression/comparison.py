import operator

from ..abc import SequenceExpression, evaluate


def _and_reduce(operator, iterable, context, event, *args, **kwargs):
	it = iter(iterable)
	a = evaluate(next(it), context, event, *args, **kwargs)

	for b in it:
		b = evaluate(b, context, event, *args, **kwargs)
		if not operator(a, b):
			return False
		a = b

	return True


class LT(SequenceExpression):
	'''
	Operator '<'
	'''

	def __call__(self, context, event, *args, **kwargs):
		return _and_reduce(operator.lt, self.Items, context, event, *args, **kwargs)


class LE(SequenceExpression):
	'''
	Operator '<='
	'''

	def __call__(self, context, event, *args, **kwargs):
		return _and_reduce(operator.le, self.Items, context, event, *args, **kwargs)


class EQ(SequenceExpression):
	'''
	Operator '=='
	'''

	def __call__(self, context, event, *args, **kwargs):
		return _and_reduce(operator.eq, self.Items, context, event, *args, **kwargs)


class NE(SequenceExpression):
	'''
	Operator '!='
	'''

	def __call__(self, context, event, *args, **kwargs):
		return _and_reduce(operator.ne, self.Items, context, event, *args, **kwargs)


class GE(SequenceExpression):
	"""
	Operator '>='
	"""

	def __call__(self, context, event, *args, **kwargs):
		return _and_reduce(operator.ge, self.Items, context, event, *args, **kwargs)


class GT(SequenceExpression):
	"""
	Operator '>'
	"""

	def __call__(self, context, event, *args, **kwargs):
		return _and_reduce(operator.gt, self.Items, context, event, *args, **kwargs)


class IS(SequenceExpression):
	"""
	Operator 'is'
	"""

	def __call__(self, context, event, *args, **kwargs):
		return _and_reduce(operator.is_, self.Items, context, event, *args, **kwargs)


class ISNOT(SequenceExpression):
	"""
	Operator 'is not'
	"""

	def __call__(self, context, event, *args, **kwargs):
		return _and_reduce(operator.is_not, self.Items, context, event, *args, **kwargs)
