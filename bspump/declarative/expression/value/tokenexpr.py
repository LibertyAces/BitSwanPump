from ..abc import Expression


class TOKEN(Expression):

	def __init__(self, expression: dict):
		super().__init__(expression)
		self.Token = expression["token"]

	def __call__(self, context, event, *args, **kwargs):
		return self.Token
