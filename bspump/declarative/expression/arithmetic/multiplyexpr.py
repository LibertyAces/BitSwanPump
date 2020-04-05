import functools

from ...abc import SequenceExpression


class MULTIPLY(SequenceExpression):
	"""
	Multiplies values in expression.
	"""

	def __call__(self, context, event, *args, **kwargs):
		return functools.reduce(
			lambda x, y: self.evaluate(x, context, event, *args, **kwargs) * self.evaluate(y, context, event, *args, **kwargs),
			self.Items
		)
