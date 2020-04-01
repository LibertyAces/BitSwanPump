from ..abc import Expression


class TOKEN(Expression):

	def __init__(self, app, expression: dict):
		super().__init__(app, expression)
		self.Token = expression["token"]

	def __call__(self, context, event, *args, **kwargs):
		return self.Token
