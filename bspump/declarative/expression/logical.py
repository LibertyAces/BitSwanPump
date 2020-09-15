import operator

from ..abc import SequenceExpression, Expression, evaluate


class AND(SequenceExpression):
	"""
	Checks if all expressions are true
	"""

	def __call__(self, context, event, *args, **kwargs):
		return self.reduce(operator.and_, context, event, *args, **kwargs)


class OR(SequenceExpression):
	"""
	Checks if at least one of the expressions is true:
	"""

	def __call__(self, context, event, *args, **kwargs):
		return self.reduce(operator.or_, context, event, *args, **kwargs)


class NOT(Expression):
	"""
	Returns inverse value of the expression
	"""

	def __init__(self, app, location, *, arg_what):
		super().__init__(app, location)
		self.Value = arg_what

	def __call__(self, context, event, *args, **kwargs):
		return not evaluate(self.Value, context, event, *args, **kwargs)
