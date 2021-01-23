from ...abc import Expression


class VALUE(Expression):
	"""
	Returns specified **scalar** value
	"""

	Attributes = {
		"Value": []
	}


	def __init__(self, app, *, value, outlet_type=None):
		super().__init__(app)
		assert(not isinstance(value, Expression))
		self.Value = value

		if outlet_type is None:
			self.OutletType = type(self.Value).__name__
		else:
			self.OutletType = outlet_type


	def __call__(self, context, event, *args, **kwargs):
		return self.Value


	def get_outlet_type(self):
		return self.OutletType
