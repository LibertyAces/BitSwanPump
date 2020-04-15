from bspump.declarative.abc import Expression


class CAST(Expression):
	"""
	Casts "value" to "type"
	"""

	def __init__(self, app, *, arg_value, arg_type):
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

	def __call__(self, context, event, *args, **kwargs):
		return self.Conversion(self.evaluate(self.Value, context, event, *args, **kwargs))
