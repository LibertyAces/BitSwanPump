from ...abc import Expression


class JOIN(Expression):
	"""
	Joins strings in "items" using "char".
	"""

	def __init__(self, app, *, arg_items, arg_delimiter=" "):
		super().__init__(app)
		self.Items = arg_items
		self.Char = arg_delimiter

	def __call__(self, context, event, *args, **kwargs):
		arr = []
		for item in self.Items:
			v = self.evaluate(item, context, event, *args, **kwargs)
			if v is None:
				return None
			arr.append(str(v))
		return self.Char.join(arr)
