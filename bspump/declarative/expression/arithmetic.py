import operator

from ..abc import SequenceExpression


class ADD(SequenceExpression):
	"""
	Add all values from expressions.
	"""

	def __call__(self, context, event, *args, **kwargs):
		return self.reduce(operator.add, context, event, *args, **kwargs)


class DIV(SequenceExpression):
	"""
	Divides values in expression
	"""

	def __call__(self, context, event, *args, **kwargs):
		return self.reduce(operator.truediv, context, event, *args, **kwargs)


class MUL(SequenceExpression):
	"""
	Multiplies values in expression.
	"""

	def __call__(self, context, event, *args, **kwargs):
		return self.reduce(operator.mul, context, event, *args, **kwargs)


class SUB(SequenceExpression):
	"""
	Subtracts values in expression
	"""

	def __call__(self, context, event, *args, **kwargs):
		return self.reduce(operator.sub, context, event, *args, **kwargs)
