from ...abc import Expression

class DICT(Expression):
	"""
	Create or update the dictionary.

		{
			"function": "DICT",
			"update": "event" | "context" | <EXPRESSION> | None
			"fields": [{FIELD_NAME: EXPRESSION}, {FIELD_NAME: EXPRESSION}, ...]
		}
	"""



	def __init__(self, app, *, arg_add, arg_with=None):
		super().__init__(None, None, None)

		self.With = arg_with
		assert(self.With in ("event", "context", None))

		self.Add = arg_add


	def __call__(self, context, event, *args, **kwargs):
		if self.With is None:
			updated_dict = {}
		elif self.With == "event":
			updated_dict = event
		elif self.With == "context":
			updated_dict = context
		elif isinstance(self.From, Expression):
			updated_dict = updated_dict(context, event, *args, **kwargs)
		else:
			raise RuntimeError("Unknown 'what' provided: '{}'".format(self.What))

		for key, value in self.Add.items():
			updated_dict[key] = self.evaluate(value, context, event, *args, **kwargs)

		return updated_dict
