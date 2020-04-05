import functools

from ...abc import SequenceExpression


class HIGHEREQ(SequenceExpression):
	"""
	Checks if all expressions are higher or equal to following one
	"""

	def __call__(self, context, event, *args, **kwargs):
		return functools.reduce(
			lambda x, y: x(context, event, *args, **kwargs) >= y(context, event, *args, **kwargs) if isinstance(x, Expression) else x >= y(context, event, *args, **kwargs),
			self.Items
		)
