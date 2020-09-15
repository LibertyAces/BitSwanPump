from ...abc import Expression, evaluate


class JOIN(Expression):

	def __init__(self, app, location, *, arg_items, arg_delimiter=" ", arg_miss=""):
		super().__init__(app, location)
		self.Items = arg_items
		self.Char = arg_delimiter
		self.Miss = arg_miss  # Could be None

	def __call__(self, context, event, *args, **kwargs):
		arr = []
		for item in self.Items:
			v = evaluate(item, context, event, *args, **kwargs)
			if v is None:
				v = evaluate(self.Miss, context, event, *args, **kwargs)
				if v is None:
					return None
			arr.append(str(v))
		return self.Char.join(arr)
