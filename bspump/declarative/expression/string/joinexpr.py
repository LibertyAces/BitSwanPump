from ...abc import Expression


class JOIN(Expression):
	"""
	Joins strings in "items" using "char".
	"""

	def __init__(self, app, *, arg_items, arg_char=" "):
		super().__init__(app)
		self.Items = arg_items
		self.Char = arg_char

	def __call__(self, context, event, *args, **kwargs):
		return self.Char.join(self.Items)
