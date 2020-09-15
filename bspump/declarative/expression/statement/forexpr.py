from ...abc import Expression, evaluate


class FOR(Expression):


	def __init__(self, app, location, *, arg_each, arg_do):
		super().__init__(app, location)
		self.Each = arg_each
		self.Do = arg_do


	def __call__(self, context, event, *args, **kwargs):
		return [
			evaluate(self.Do, context, event, item, *args, **kwargs)
			for item in evaluate(self.Each, context, event, *args, **kwargs)
		]
