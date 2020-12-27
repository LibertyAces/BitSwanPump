import operator

from ..abc import SequenceExpression


class ADD(SequenceExpression):
	"""
	Add all values from expressions.
	"""

	Attributes = {
		"Items": [
			'si64', 'si8', 'si16', 'si32', 'si64', 'si128', 'si256',
			'ui8', 'ui16', 'ui32', 'ui64', 'ui128', 'ui256',
		]
	}

	def __call__(self, context, event, *args, **kwargs):
		return self.reduce(operator.add, context, event, *args, **kwargs)

	def get_output_type(self):
		return _get_output_type_from_first(self.Items)


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


class MOD(SequenceExpression):
	"""
	Modules values in expression.
	"""

	def __call__(self, context, event, *args, **kwargs):
		return self.reduce(operator.mod, context, event, *args, **kwargs)


def _get_output_type_from_first(items):
	if len(items) == 0:
		return int.__name__
	# Take the type of the first item in the list
	return items[0].get_output_type()
