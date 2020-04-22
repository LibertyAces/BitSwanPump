import logging
import os
import inspect

import yaml

from . import expression

###

L = logging.getLogger(__name__)

###


class ExpressionBuilder(object):
	"""
	Builds an expression from configuration.
	"""

	def __init__(self, app, basedir='.'):
		self.App = app
		self.BaseDir = basedir

		self.ExpressionClasses = {}

		# Register the common expression module
		self.register_module(expression)


	def register_module(self, module):
		for name, expression_class in inspect.getmembers(module, inspect.isclass):
			self.ExpressionClasses[name] = expression_class

	def register_class(self, class_name, expression_class):
		self.ExpressionClasses[class_name] = expression_class


	def read(self, identifier):

		# TODO: Allow user code to register other sources of the YAML files (eg. MongoDB)

		# Try to load YAML from a disk
		fname = os.path.join(self.BaseDir, identifier + '.yaml')
		if os.path.exists(fname):
			with open(fname, 'r') as f:
				return f.read()

		raise RuntimeError("Cannot read '{}' YAML declaration".format(identifier))


	def parse(self, declaration):
		if isinstance(declaration, str) and declaration.startswith('---'):
			pass
		else:
			declaration = self.read(declaration)

		loader = yaml.Loader(declaration)

		# Register the constructor for each registered expression class
		for name in self.ExpressionClasses:
			loader.add_constructor("!{}".format(name), self._constructor)

		loader.add_constructor("!INCLUDE", self._construct_include)

		try:
			expression = loader.get_single_data()
		finally:
			loader.dispose()

		return expression



	def _construct_include(self, loader: yaml.Loader, node: yaml.Node):
		"""Include file referenced at node."""

		identifier = loader.construct_scalar(node)
		declaration = self.read(identifier)
		return yaml.load(declaration)


	def _constructor(self, loader, node):
		assert(node.tag[0] == '!')
		xclass = self.ExpressionClasses[node.tag[1:]]

		try:
			if isinstance(node, yaml.ScalarNode):
				value = loader.construct_scalar(node)
				return xclass(self.App, value=value)

			elif isinstance(node, yaml.SequenceNode):
				value = loader.construct_sequence(node)
				return xclass(self.App, sequence=value)

			elif isinstance(node, yaml.MappingNode):
				value = loader.construct_mapping(node)
				return xclass(self.App, **dict(('arg_' + k, v) for k, v in value.items()))

		except Exception:
			L.exception("Error when constructing '{}'".format(xclass))
			raise

		raise RuntimeError("Unsupported type '{}'".format(node))
