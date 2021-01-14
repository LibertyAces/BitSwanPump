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
		self.App = app
		self.Items = arg_items
		self.Char = arg_delimiter

		if not isinstance(arg_miss, Expression):
			self.Miss = VALUE(app, value=arg_miss)
		else:
			self.Miss = arg_miss

	def initialize(self):
		for index in range(0, len(self.Items)):
			if not isinstance(self.Items[index], Expression):
				self.Items[index] = VALUE(self.App, value=self.Items[index])

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
