from ...abc import Expression, evaluate


class WHEN(Expression):
	"""
	Checks "if" condition passes - it is an `if` on steroids ;-)

	!WHEN
	- is:
		!EQ
		- !ITEM EVENT eggs
		- 2
	then: eggs

	- is:
		!LT
		- 9
		- !ITEM EVENT potatoes
		- 11
	then: potatoes

	- else:
		Nah

	"""

	Attributes = {
		"Items": [],
	}

	def __init__(self, app, *, sequence):
		super().__init__(app)
		self.Items = sequence

	def __call__(self, context, event, *args, **kwargs):
		for branch in self.Items:
			expr_test = branch.get('test')
			if expr_test is not None:

				res = evaluate(expr_test, context, event, *args, **kwargs)
				if res:
					expr_then = branch.get('then', True)
					return evaluate(expr_then, context, event, *args, **kwargs)

				else:
					continue

			expr_else = branch.get('else')
			if expr_else is not None:
				return evaluate(expr_else, context, event, *args, **kwargs)

		return False
