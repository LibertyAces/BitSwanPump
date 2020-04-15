from ...abc import SequenceExpression


class TUPLE(SequenceExpression):

	def __call__(self, context, event, *args, **kwargs):
		return tuple(self.evaluate(item, context, event, *args, **kwargs) for item in self.Items)
