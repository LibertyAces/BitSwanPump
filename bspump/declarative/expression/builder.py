import importlib

from .value.tokenexpr import TOKEN


class ExpressionBuilder(object):

	@classmethod
	def build(cls, app, expression, module_name="bspump.declarative.expression"):
		if isinstance(expression, dict):
			_module = importlib.import_module(module_name)
			_class = getattr(_module, expression["class"])
			return _class(app, expression)
		else:
			return TOKEN(app, {"token": expression})
