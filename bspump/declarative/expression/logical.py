import operator

from ..abc import SequenceExpression, Expression, evaluate


def _and_reduce(operator, iterable, context, event, *args, **kwargs):
	it = iter(iterable)
	a = evaluate(next(it), context, event, *args, **kwargs)
	if not a:
		return False

	for b in it:
		b = evaluate(b, context, event, *args, **kwargs)
		if b is None or not operator(a, b):
			return False
		a = b

	return True


def _or_reduce(operator, iterable, context, event, *args, **kwargs):
	it = iter(iterable)
	a = evaluate(next(it), context, event, *args, **kwargs)
	if a:
		return True

	for b in it:
		b = evaluate(b, context, event, *args, **kwargs)
		if b is None:
			continue
		if operator(a, b):
			return True
		a = b

	return False


class AND(SequenceExpression):
	"""
	Checks if all expressions are true
	"""

	def __call__(self, context, event, *args, **kwargs):
		return _and_reduce(operator.and_, self.Items, context, event, *args, **kwargs)


class OR(SequenceExpression):
	"""
	Checks if at least one of the expressions is true:
	"""

	def __call__(self, context, event, *args, **kwargs):
		return _or_reduce(operator.or_, self.Items, context, event, *args, **kwargs)


class NOT(Expression):
	"""
	Returns inverse value of the expression
	"""

	def __init__(self, app, *, arg_what):
		super().__init__(app)
		self.Value = arg_what

	def __call__(self, context, event, *args, **kwargs):
		try:
			return not evaluate(self.Value, context, event, *args, **kwargs)
		except TypeError:
			# Incompatible types included
			return None
