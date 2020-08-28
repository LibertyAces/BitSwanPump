import operator

from ..abc import SequenceExpression, evaluate


def _and_reduce(operator, iterable):
	it = iter(iterable)
	a = next(it)

	for b in it:
		if not operator(a, b):
			return False
		a = b

	return True


class LT(SequenceExpression):
	'''
	Operator '<'
	'''

	def __call__(self, context, event, *args, **kwargs):
		return _and_reduce(
			operator.lt,
			[evaluate(item, context, event, *args, **kwargs) for item in self.Items]
		)


class LE(SequenceExpression):
	'''
	Operator '<='
	'''

	def __call__(self, context, event, *args, **kwargs):
		return _and_reduce(
			operator.le,
			[evaluate(item, context, event, *args, **kwargs) for item in self.Items]
		)


class EQ(SequenceExpression):
	'''
	Operator '=='
	'''

	def __call__(self, context, event, *args, **kwargs):
		return _and_reduce(
			operator.eq,
			[evaluate(item, context, event, *args, **kwargs) for item in self.Items]
		)


class NE(SequenceExpression):
	'''
	Operator '!='
	'''

	def __call__(self, context, event, *args, **kwargs):
		return _and_reduce(
			operator.ne,
			[evaluate(item, context, event, *args, **kwargs) for item in self.Items]
		)


class GE(SequenceExpression):
	"""
	Operator '>='
	"""

	def __call__(self, context, event, *args, **kwargs):
		return _and_reduce(
			operator.ge,
			[evaluate(item, context, event, *args, **kwargs) for item in self.Items]
		)


class GT(SequenceExpression):
	"""
	Operator '>'
	"""

	def __call__(self, context, event, *args, **kwargs):
		return _and_reduce(
			operator.gt,
			[evaluate(item, context, event, *args, **kwargs) for item in self.Items]
		)


class IS(SequenceExpression):
	"""
	Operator 'is'
	"""

	def __call__(self, context, event, *args, **kwargs):
		return _and_reduce(
			operator.is_,
			[evaluate(item, context, event, *args, **kwargs) for item in self.Items]
		)


class ISNOT(SequenceExpression):
	"""
	Operator 'is not'
	"""

	def __call__(self, context, event, *args, **kwargs):
		return _and_reduce(
			operator.is_not,
			[evaluate(item, context, event, *args, **kwargs) for item in self.Items]
		)
