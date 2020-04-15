from bspump.declarative.abc import Expression


class CAST(Expression):
	"""
	Casts "value" to "type"
	"""

	def __init__(self, app, *, arg_value, arg_type):
		super().__init__(app)
		self.Value = arg_value
		self.Type = arg_type

	def __call__(self, context, event, *args, **kwargs):
		_type = self.evaluate(self.Type, context, event, *args, **kwargs)
		if _type == "int":
			return int(self.evaluate(self.Value, context, event, *args, **kwargs))
		elif _type == "float":
			return float(self.evaluate(self.Value, context, event, *args, **kwargs))
		elif _type == "str":
			return str(self.evaluate(self.Value, context, event, *args, **kwargs))
		elif _type == "dict":
			return dict(self.evaluate(self.Value, context, event, *args, **kwargs))
		elif _type == "list":
			return list(self.evaluate(self.Value, context, event, *args, **kwargs))
		else:
			raise RuntimeError("Unsupported type '{}' found in CAST expression.".format(_type))
