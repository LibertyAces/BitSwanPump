from ...abc import Expression

class ITEM(Expression):
	"""
	Obtains value of "field" from a dictionary (event/context):
	"""

	def __init__(self, app, *, arg_name = None, arg_default = None, value = None):
		super().__init__(None, None, None)
		
		field = arg_name if arg_name is not None else value
		if field is None:
			raise ValueError("Field name was not provided")
		self.FieldType, self.FieldName = field.split('.', 2)

		assert(self.FieldType in ('context', 'event'))

		self.Default = arg_default
		#TODO: if isinstance(self.Default, dict):
		# 	self.Default = ExpressionBuilder.build(app, expression_class_registry, self.Default)


	def __call__(self, context, event, *args, **kwargs):
		
		if self.FieldType == "event":
			return event.get(self.FieldName, self.Default)
		
		elif self.FieldType == "context":
			return context.get(self.FieldName, self.Default)
		
		else:
			return self.Default
