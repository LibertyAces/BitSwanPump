from bspump.declarative.abc import Expression


class CAST(Expression):
	"""
	Casts "value" to "type"
	"""

	def __init__(self, app, *, arg_value, arg_type, arg_default=None):
		super().__init__(app)
		self.Value = arg_value

		# Detect type cast function
		if arg_type == "int":
			self.Conversion = int
		elif arg_type == "float":
			self.Conversion = float
		elif arg_type == "str":
			self.Conversion = str
		elif arg_type == "dict":
			self.Conversion = dict
		elif arg_type == "list":
			self.Conversion = list
		else:
			raise RuntimeError("Unsupported type '{}' found in CAST expression.".format(arg_type))

		self.Default = arg_default


	def __call__(self, context, event, *args, **kwargs):
		try:
			return self.Conversion(self.evaluate(self.Value, context, event, *args, **kwargs))
		except ValueError:
			if self.Default is None:
				return None
			return self.evaluate(self.Default, context, event, *args, **kwargs)
