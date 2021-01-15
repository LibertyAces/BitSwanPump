from ...abc import Expression


class VALUE(Expression):
	"""
	Returns specified **scalar** value
	"""

	Attributes = {
		"Value": []
	}


	def __init__(self, app, *, value):
		super().__init__(app)
		assert(not isinstance(value, Expression))

		self.Value = value


	def __call__(self, context, event, *args, **kwargs):
		return self.Value


	def get_outlet_type(self):
		return type(self.Value).__name__
