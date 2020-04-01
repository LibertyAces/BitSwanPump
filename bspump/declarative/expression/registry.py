import importlib
import inspect


class ExpressionClassRegistry(object):
	"""
	Register expression classes, that are then going to
	be instantiated according to the expression configuration.
	"""

	def __init__(self, default_module_name="bspump.declarative.expression"):
		self.Classes = {}
		self.register_module(default_module_name)

	def register_module(self, module_name):
		_module = importlib.import_module(module_name)
		for name, _class in inspect.getmembers(_module, inspect.isclass):
			self.Classes[name] = _class

	def register_class(self, class_name, _class):
		self.Classes[class_name] = _class

	def get_class(self, class_name):
		return self.Classes.get(class_name)
