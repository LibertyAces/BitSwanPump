from ...abc import Expression


class FOR(Expression):


	def __init__(self, app, *, arg_each, arg_do):
		super().__init__(app)
		self.Each = arg_each
		self.Do = arg_do


	def __call__(self, context, event, *args, **kwargs):
		return [
			self.evaluate(self.Do, context, event, item, *args, **kwargs)
			for item in self.evaluate(self.Each, context, event, *args, **kwargs)
		]
