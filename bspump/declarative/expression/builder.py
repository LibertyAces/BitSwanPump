from .value.tokenexpr import TOKEN


class ExpressionBuilder(object):
	"""
	Builds an expression from configuration.
	If the expression is not a dictionary, TOKEN expression is instantiated.
	"""

	@classmethod
	def build(cls, app, expression_class_registry, expression):
		if isinstance(expression, dict):
			_class = expression_class_registry.get_class(expression["class"])
			return _class(app, expression_class_registry, expression)
		else:
			return TOKEN(app, expression_class_registry, {"token": expression})
