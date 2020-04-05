from ...abc import Expression


class ITEM(Expression):
	"""
	Obtains value of "item" from a dictionary (event/context):
	"""

	def __init__(self, app, *, arg_name=None, arg_default=None, value=None):
		super().__init__(app)
		
		field = arg_name if arg_name is not None else value
		if field is None:
			raise ValueError("Field name was not provided")
		self.FieldType, self.FieldName = field.split('.', 2)

		assert(self.FieldType in ('context', 'event'))

		self.Default = arg_default


	def __call__(self, context, event, *args, **kwargs):
		
		value = _DefaultValue

		if self.FieldType == "event":
			value = event.get(self.FieldName, _DefaultValue)
		
		elif self.FieldType == "context":
			value = context.get(self.FieldName, _DefaultValue)
		
		if value == _DefaultValue:
			# This deffers evaluation of the default value to the moment, when it is really needed
			return self.evaluate(self.Default, context, event, *args, **kwargs)
		else:
			return value


class _DefaultValue:
	pass
