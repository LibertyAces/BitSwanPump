import operator

from ..abc import SequenceExpression, Expression, evaluate


def _oper_reduce(operator, iterable, context, event, *args, **kwargs):
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
		return _oper_reduce(operator.lt, self.Items, context, event, *args, **kwargs)


class LE(SequenceExpression):
	'''
	Operator '<='
	'''

	def __call__(self, context, event, *args, **kwargs):
		return _oper_reduce(operator.le, self.Items, context, event, *args, **kwargs)


class EQ(SequenceExpression):
	'''
	Operator '=='
	'''

	def __call__(self, context, event, *args, **kwargs):
		return _oper_reduce(operator.eq, self.Items, context, event, *args, **kwargs)


	def optimize(self):
		if len(self.Items) == 2 and isinstance(self.Items[1], (str, int, float)):
			return EQ_optimized_simple(self)
		return self


class EQ_optimized_simple(EQ):

	def __init__(self, orig):
		super().__init__(orig.App, sequence=orig.Items)
		self.A = self.Items[0]
		assert isinstance(self.A, Expression)
		self.B = self.Items[1]
		assert isinstance(self.B, (str, int, float))

	def __call__(self, context, event, *args, **kwargs):
		return self.A(context, event, *args, **kwargs) == self.B


class NE(SequenceExpression):
	'''
	Operator '!='
	'''

	def __call__(self, context, event, *args, **kwargs):
		return _oper_reduce(operator.ne, self.Items, context, event, *args, **kwargs)


class GE(SequenceExpression):
	"""
	Operator '>='
	"""

	def __call__(self, context, event, *args, **kwargs):
		return _oper_reduce(operator.ge, self.Items, context, event, *args, **kwargs)


class GT(SequenceExpression):
	"""
	Operator '>'
	"""

	def __call__(self, context, event, *args, **kwargs):
		return _oper_reduce(operator.gt, self.Items, context, event, *args, **kwargs)


class IS(SequenceExpression):
	"""
	Operator 'is'
	"""

	def __call__(self, context, event, *args, **kwargs):
		return _oper_reduce(operator.is_, self.Items, context, event, *args, **kwargs)


class ISNOT(SequenceExpression):
	"""
	Operator 'is not'
	"""

	def __call__(self, context, event, *args, **kwargs):
		return _oper_reduce(operator.is_not, self.Items, context, event, *args, **kwargs)
