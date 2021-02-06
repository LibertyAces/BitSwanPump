from ...abc import SequenceExpression, evaluate


class FIRST(SequenceExpression):

	Category = 'Statements'

	def __call__(self, context, event, *args, **kwargs):
		for item in self.Items:
			res = evaluate(item, context, event, *args, **kwargs)
			if res is not None:
				return res
