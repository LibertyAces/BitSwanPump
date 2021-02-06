from ...abc import Expression


class UPPER(Expression):

	Attributes = {
		"Value": ["str"],
	}

	Category = "String"


	def __init__(self, app, *, arg_what):
		super().__init__(app)
		self.Value = arg_what

	def get_outlet_type(self):
		return str.__name__

	def consult_inlet_type(self, key, child):
		return str.__name__

	def __call__(self, context, event, *args, **kwargs):
		try:
			return self.Value(context, event, *args, **kwargs).upper()
		except AttributeError:
			return None
