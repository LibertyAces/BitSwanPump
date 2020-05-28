import operator

from ..abc import SequenceExpression


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
			[self.evaluate(item, context, event, *args, **kwargs) for item in self.Items]
		)


class LE(SequenceExpression):
	'''
	Operator '<='
	'''

	def __call__(self, context, event, *args, **kwargs):
		return _and_reduce(
			operator.le,
			[self.evaluate(item, context, event, *args, **kwargs) for item in self.Items]
		)


class EQ(SequenceExpression):
	'''
	Operator '=='
	'''

	def __call__(self, context, event, *args, **kwargs):
		return _and_reduce(
			operator.eq,
			[self.evaluate(item, context, event, *args, **kwargs) for item in self.Items]
		)


class NE(SequenceExpression):
	'''
	Operator '!='
	'''

	def __call__(self, context, event, *args, **kwargs):
		return _and_reduce(
			operator.ne,
			[self.evaluate(item, context, event, *args, **kwargs) for item in self.Items]
		)


class GE(SequenceExpression):
	"""
	Operator '>='
	"""

	def __call__(self, context, event, *args, **kwargs):
		return _and_reduce(
			operator.ge,
			[self.evaluate(item, context, event, *args, **kwargs) for item in self.Items]
		)


class GT(SequenceExpression):
	"""
	Operator '>'
	"""

	def __call__(self, context, event, *args, **kwargs):
		return _and_reduce(
			operator.gt,
			[self.evaluate(item, context, event, *args, **kwargs) for item in self.Items]
		)


class IS(SequenceExpression):
	"""
	Operator 'is'
	"""

	def __call__(self, context, event, *args, **kwargs):
		return _and_reduce(
			operator.is_,
			[self.evaluate(item, context, event, *args, **kwargs) for item in self.Items]
		)


class ISNOT(SequenceExpression):
	"""
	Operator 'is not'
	"""

	def __call__(self, context, event, *args, **kwargs):
		return _and_reduce(
			operator.is_not,
			[self.evaluate(item, context, event, *args, **kwargs) for item in self.Items]
		)
