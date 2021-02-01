from ...abc import Expression
from ..value.valueexpr import VALUE


class JOIN(Expression):

	Attributes = {
		"Char": ["str"],
		"Miss": ["*"],  # TODO: This ...
	}

	Category = "String"


	def __init__(self, app, *, arg_items, arg_delimiter=" ", arg_miss=""):
		super().__init__(app)
		self.App = app

		self.Items = arg_items
		self.ItemsNormalized = []

		self.Char = arg_delimiter

		if not isinstance(arg_miss, Expression):
			self.Miss = VALUE(app, value=arg_miss)
		else:
			self.Miss = arg_miss


	def set(self, key, value):
		setattr(self, key, value)

		if "Item" in key:
			self.ItemsNormalized[int(key[4:])] = value


	def initialize(self):

		for n, item in enumerate(self.Items):

			if not isinstance(item, Expression):
				item = VALUE(self.App, value=item)

			attr_name = 'Item{}'.format(n)
			setattr(self, attr_name, item)
			self.Attributes[attr_name] = str.__name__

			self.ItemsNormalized.append(item)


	def __call__(self, context, event, *args, **kwargs):
		arr = []
		for item in self.ItemsNormalized:
			v = item(context, event, *args, **kwargs)
			if v is None:
				v = self.Miss(context, event, *args, **kwargs)
				if v is None:
					return None
			arr.append(str(v))
		return self.Char.join(arr)
