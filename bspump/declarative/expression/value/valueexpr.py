from ...abc import Expression
from ...abc import SequenceExpression


class VALUE(Expression):
	"""
	Returns specified **scalar** value
	"""

	def __init__(self, app, *, value):
		super().__init__(app)
		self.Value = value
		assert(not isinstance(self.Value, Expression))

	def __call__(self, context, event, *args, **kwargs):
		return self.Value


class TUPLE(SequenceExpression):

	def __call__(self, context, event, *args, **kwargs):
		return tuple(self.evaluate(item, context, event, *args, **kwargs) for item in self.Items)
