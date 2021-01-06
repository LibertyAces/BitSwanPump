from ...abc import Expression, evaluate
from ..value.valueexpr import VALUE


class JOIN(Expression):

	Attributes = {
		"Items": [],  # TODO: This ...
		"Char": ["*"],  # TODO: This ...
		"Miss": ["*"],  # TODO: This ...
	}

	def __init__(self, app, *, arg_items, arg_delimiter=" ", arg_miss=""):
		super().__init__(app)
		self.Items = arg_items
		self.Char = arg_delimiter

		if not isinstance(arg_miss, Expression):
			self.Miss = VALUE(app, value=arg_miss)
		else:
			self.Miss = arg_miss

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
