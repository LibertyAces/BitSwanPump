from ...abc import SequenceExpression, evaluate


class TUPLE(SequenceExpression):

	def __call__(self, context, event, *args, **kwargs):
		return tuple(evaluate(item, context, event, *args, **kwargs) for item in self.Items)
