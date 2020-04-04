from .value.valueexpr import VALUE


class ExpressionBuilder(object):
	"""
	Builds an expression from configuration.
	If the expression is not a dictionary, VALUE expression is instantiated.
	"""

	@classmethod
	def build(cls, app, expression_class_registry, expression):
		if isinstance(expression, dict):
			fnctclass = expression_class_registry.get_class(expression["function"])
			return fnctclass(app, expression_class_registry, expression)
		
		else:
			# Shortcuts goes here
			return VALUE(app, expression_class_registry, {"value": expression})
