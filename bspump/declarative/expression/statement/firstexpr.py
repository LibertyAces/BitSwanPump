from ...abc import SequenceExpression


class FIRST(SequenceExpression):

	def __call__(self, context, event, *args, **kwargs):
		for item in self.Items:
			res = self.evaluate(item, context, event, *args, **kwargs)
			if res is not None:
				return res
