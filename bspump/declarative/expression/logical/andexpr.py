import functools

from ...abc import SequenceExpression


class AND(SequenceExpression):
	"""
	Checks if all expressions are true
	"""

	def __call__(self, context, event, *args, **kwargs):
		return functools.reduce(
			lambda x, y: self.evaluate(x, context, event, *args, **kwargs) and self.evaluate(y, context, event, *args, **kwargs),
			self.Items
		)
