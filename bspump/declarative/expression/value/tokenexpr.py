from ..abc import Expression


class TOKEN(Expression):
	"""
	Returns specified value:

		{
			"class": "TOKEN",
			"token": "token"
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		self.Token = expression["token"]

	def __call__(self, context, event, *args, **kwargs):
		return self.Token
