import operator

from ..abc import SequenceExpression


class LT(SequenceExpression):
	'''
	Operator '<'
	'''

	def __call__(self, context, event, *args, **kwargs):
		return self.reduce(operator.lt, context, event, *args, **kwargs)


class LE(SequenceExpression):
	'''
	Operator '<='
	'''

	def __call__(self, context, event, *args, **kwargs):
		return self.reduce(operator.le, context, event, *args, **kwargs)

class EQ(SequenceExpression):
	'''
	Operator '=='
	'''

	def __call__(self, context, event, *args, **kwargs):
		return self.reduce(operator.eq, context, event, *args, **kwargs)

class NE(SequenceExpression):
	'''
	Operator '!='
	'''

	def __call__(self, context, event, *args, **kwargs):
		return self.reduce(operator.ne, context, event, *args, **kwargs)

class GE(SequenceExpression):
	"""
	Operator '>='
	"""

	def __call__(self, context, event, *args, **kwargs):
		return self.reduce(operator.ge, context, event, *args, **kwargs)

class GT(SequenceExpression):
	"""
	Operator '>'
	"""

	def __call__(self, context, event, *args, **kwargs):
		return self.reduce(operator.gt, context, event, *args, **kwargs)
