import functools

from ...abc import SequenceExpression

class OR(SequenceExpression):
	"""
	Checks if at least one of the expressions is true:
	"""

	def __call__(self, context, event, *args, **kwargs):
		return functools.reduce(
			lambda x, y: self.evaluate(x, context, event, *args, **kwargs) or self.evaluate(y, context, event, *args, **kwargs),
			self.Items
		)
