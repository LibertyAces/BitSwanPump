import logging
import inspect

import yaml

from . import expression

from .libraries import FileDeclarationLibrary
from .declerror import DeclarationError
from .abc import Expression
from .expression.value.valueexpr import VALUE

###

L = logging.getLogger(__name__)

###


class ExpressionBuilder(object):
	"""
	Builds an expression from configuration.
	"""

	def __init__(self, app, libraries=None):
		self.App = app
		self.ExpressionClasses = {}
		self.Identifier = None

		self.Config = {}

		if libraries is None:
			self.Libraries = [FileDeclarationLibrary()]
		else:
			self.Libraries = libraries

		# Register the common expression module
		self.register_module(expression)

	def register_module(self, module):
		for class_name, expression_class in inspect.getmembers(module, inspect.isclass):
			self.register_class(class_name, expression_class)

	def register_class(self, class_name, expression_class):
		class_name = class_name.replace('_', '.')
		self.ExpressionClasses[class_name] = expression_class

	def add_config_value(self, key, value):
		self.Config[key] = value

	def update_config(self, config):
		self.Config.update(config)

	def read(self, identifier):
		# Read declaration from available declarations libraries
		for declaration_library in self.Libraries:
			declaration = declaration_library.read(identifier)
			if declaration is not None:
				return declaration

		raise RuntimeError("Cannot find '{}' YAML declaration in libraries".format(identifier))


	def parse(self, declaration, source_name=None):
		"""
		Returns a list of expression from the loaded declaration.
		:param declaration:
		:param source_name:
		:return:
		"""

		self.Identifier = None
		if isinstance(declaration, str) and declaration.startswith('---'):
			pass
		else:
			self.Identifier = declaration
			declaration = self.read(self.Identifier)

		loader = yaml.Loader(declaration)
		if source_name is not None:
			loader.name = source_name

		# Register the constructor for each registered expression class
		for name in self.ExpressionClasses:
			loader.add_constructor("!{}".format(name), self._constructor)

		loader.add_constructor("!INCLUDE", self._construct_include)
		loader.add_constructor("!CONFIG", self._construct_config)

		expressions = []
		try:
			# Build syntax trees for each expression
			while loader.check_data():
				expression = loader.get_data()

				# Run initialize for the expression and any instance inside
				for parent, key, obj in self._walk(expression):

					if not isinstance(obj, Expression):
						continue

					obj.initialize()

				expressions.append(expression)

		except yaml.scanner.ScannerError as e:
			raise DeclarationError("Syntax error in declaration: {}".format(e))

		except yaml.constructor.ConstructorError as e:
			raise DeclarationError("Unknown declarative expression: {}".format(e))

		finally:
			loader.dispose()

		return expressions


	def _walk(self, expression):
		if isinstance(expression, Expression):

			for parent, key, obj in expression.walk():
				yield (parent, key, obj)

				if isinstance(obj, (dict, list)):
					for _parent, _key, _obj in self._walk(obj):
						yield (_parent, _key, _obj)

		elif isinstance(expression, dict):

			for _key, _expression in expression.items():
				for parent, key, obj in self._walk(_expression):
					yield (parent, key, obj)

		elif isinstance(expression, list):

			for _expression in expression:
				for parent, key, obj in self._walk(_expression):
					yield (parent, key, obj)

		elif isinstance(expression, (str, int, float)):
			return

		raise NotImplementedError("Initialization not implemented for '{}'.".format(expression))


	def _construct_include(self, loader: yaml.Loader, node: yaml.Node):
		"""Include file referenced at node."""

		identifier = loader.construct_scalar(node)
		declaration = self.read(identifier)
		# Include can be only one expression
		return self.parse(declaration, identifier)[0]


	def _construct_config(self, loader: yaml.Loader, node: yaml.Node):
		key = loader.construct_scalar(node)
		return self.Config.get(key)


	def _constructor(self, loader, node):
		assert(node.tag[0] == '!')
		xclass = self.ExpressionClasses[node.tag[1:]]

		location = node.start_mark
		if self.Identifier is not None:
			# https://github.com/yaml/pyyaml/blob/4c2e993321ad29a02a61c4818f3cef9229219003/lib3/yaml/reader.py
			location = location.replace("<unicode string>", str(self.Identifier))

		try:
			if isinstance(node, yaml.ScalarNode):
				value = loader.construct_scalar(node)
				obj = xclass(app=self.App, value=value)

			elif isinstance(node, yaml.SequenceNode):
				value = loader.construct_sequence(node)
				obj = xclass(app=self.App, sequence=value)

			elif isinstance(node, yaml.MappingNode):
				value = loader.construct_mapping(node)
				obj = xclass(app=self.App, **dict(('arg_' + k, v) for k, v in value.items()))

			else:
				raise RuntimeError("Unsupported node type '{}'".format(node))

			obj.set_location(location)
			obj.Node = node
			return obj

		except TypeError as e:
			raise DeclarationError("Type error {}\n{}\n".format(e, node.start_mark))

		except Exception as e:
			L.exception("Error in expression")
			raise DeclarationError("Invalid expression at {}\n{}".format(node.start_mark, e))
