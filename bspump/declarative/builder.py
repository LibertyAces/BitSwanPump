import logging
import inspect

import yaml

from .declerror import DeclarationError
from .abc import Expression

from .expression.value.valueexpr import VALUE
from .expression.statement.funexpr import FUNCTION

from .expression.utility.castexpr import CAST
from .expression.statement.selfexpr import SELF

###

L = logging.getLogger(__name__)

###


class IncludeNeeded(Exception):

	def __init__(self, identifier):
		super().__init__()
		self.Identifier = identifier


class ExpressionBuilder(object):
	"""
	Builds an expression from configuration.
	"""

	def __init__(self, app, library=None, include_paths=None):
		self.App = app
		self.ExpressionClasses = {}
		self.Identifier = None

		self.Config = {}
		self.Library = library

		if include_paths is None:
			self.IncludePaths = ["/include"]

		else:
			self.IncludePaths = include_paths
			assert isinstance(include_paths, list)

		# Cache for loaded includes during the parsing
		self.LoadedIncludes = {}

		# Register the common expression module
		from . import expression
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

	async def read(self, identifier):

		if self.Library is None:
			raise RuntimeError("Cannot read '{}' in builder, ASAB library is not provided".format(identifier))

		# Read declaration from available declarations libraries
		for include_path in self.IncludePaths:
			declaration = await self.Library.read("{}/{}.yaml".format(include_path, identifier))

			if declaration is not None:
				return declaration.read().decode("utf-8")

		raise RuntimeError("Cannot find '{}' YAML declaration in libraries".format(identifier))


	async def parse(self, declaration, source_name=None):
		"""
		Returns a list of expressions from the loaded declaration.
		:param declaration:
		:param source_name:
		:return:
		"""
		self.Identifier = None

		if isinstance(declaration, str) and declaration.startswith('---'):
			pass

		else:
			self.Identifier = declaration
			declaration = await self.read(declaration)

		while True:

			loader = yaml.Loader(declaration)
			if source_name is not None:
				loader.name = source_name

			# Register the constructor for each registered expression class
			for name in self.ExpressionClasses:
				loader.add_constructor("!{}".format(name), self._constructor)

			loader.add_constructor("!INCLUDE", self._construct_include)
			loader.add_constructor("!CONFIG", self._construct_config)

			loader.add_constructor("tag:yaml.org,2002:ui256", self._construct_scalar)
			loader.add_constructor("tag:yaml.org,2002:ui128", self._construct_scalar)
			loader.add_constructor("tag:yaml.org,2002:ui64", self._construct_scalar)
			loader.add_constructor("tag:yaml.org,2002:ui32", self._construct_scalar)
			loader.add_constructor("tag:yaml.org,2002:ui16", self._construct_scalar)
			loader.add_constructor("tag:yaml.org,2002:ui8", self._construct_scalar)

			loader.add_constructor("tag:yaml.org,2002:si256", self._construct_scalar)
			loader.add_constructor("tag:yaml.org,2002:si128", self._construct_scalar)
			loader.add_constructor("tag:yaml.org,2002:si64", self._construct_scalar)
			loader.add_constructor("tag:yaml.org,2002:si32", self._construct_scalar)
			loader.add_constructor("tag:yaml.org,2002:si16", self._construct_scalar)
			loader.add_constructor("tag:yaml.org,2002:si8", self._construct_scalar)

			loader.add_constructor("tag:yaml.org,2002:fp128", self._construct_scalar)
			loader.add_constructor("tag:yaml.org,2002:fp64", self._construct_scalar)
			loader.add_constructor("tag:yaml.org,2002:fp32", self._construct_scalar)
			loader.add_constructor("tag:yaml.org,2002:fp16", self._construct_scalar)

			loader.add_constructor("tag:yaml.org,2002:str", self._construct_scalar)

			try:
				expressions = []

				# Build syntax trees for each expression
				while loader.check_data():
					expression = loader.get_data()

					# Run initialize for the expression and any instance inside
					for parent, key, obj in self._walk(expression):

						if not isinstance(obj, Expression):
							continue

						if source_name != "<INCLUDE>":

							if isinstance(obj, SELF):
								# Implement a self-reference or Y-Combinator
								obj.initialize(expression)
							else:
								obj.initialize()

					expressions.append(expression)

			except yaml.scanner.ScannerError as e:
				raise DeclarationError("Syntax error in declaration: {}".format(e))

			except yaml.constructor.ConstructorError as e:
				raise DeclarationError("Unknown declarative expression: {}".format(e))

			except IncludeNeeded as e:
				# If include is needed, load its declaration to the loaded include cache
				include_declaration = await self.read(e.Identifier)
				parsed_declaration = await self.parse(include_declaration, "<INCLUDE>")

				# Include can be only one expression
				self.LoadedIncludes[e.Identifier] = parsed_declaration[0]
				continue

			finally:
				loader.dispose()

			return expressions


	async def parse_ext(self, declaration, source_name=None):
		'''
		Wrap top-level declaration into a function, value etc.
		This is likely intermediate (not a final) implementation.
		'''
		result = []
		for expr in await self.parse(declaration, source_name=source_name):

			if isinstance(expr, (VALUE, FUNCTION)):
				result.append(expr)
				continue

			if isinstance(expr, Expression):
				fun_expr = FUNCTION(self.App, arg_apply=expr, arg_name="main")
				fun_expr.set_location(expr.Location)
				result.append(fun_expr)
				continue

			if isinstance(expr, (bool, int, float, str, set, list, dict)):
				expr = VALUE(self.App, value=expr)
				# Fake the location string
				expr.set_location('  at line 1, column 1:\n{}\n^'.format(declaration[:20]))
				result.append(expr)
				continue

			raise NotImplementedError("Top-level type '{}' not supported".format(type(expr)))

		return result


	def _walk(self, expression):
		if expression is None:
			return

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

		elif isinstance(expression, (list, set, frozenset)):

			for _expression in expression:
				for parent, key, obj in self._walk(_expression):
					yield (parent, key, obj)

		elif isinstance(expression, (str, int, float, tuple)):
			return

		else:
			raise NotImplementedError("Walk not implemented for '{}'.".format(expression))


	def _construct_include(self, loader: yaml.Loader, node: yaml.Node):
		"""Include file referenced at node."""

		identifier = loader.construct_scalar(node)

		try:
			return self.LoadedIncludes[identifier]

		except KeyError:
			raise IncludeNeeded(identifier)


	def _construct_config(self, loader: yaml.Loader, node: yaml.Node):
		key = loader.construct_scalar(node)
		return self.Config.get(key)


	def _constructor(self, loader, node):
		assert node.tag[0] == '!'
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

		except IncludeNeeded as e:
			raise e

		except TypeError as e:
			raise DeclarationError("Type error {}\n{}\n".format(e, node.start_mark))

		except Exception as e:
			L.exception("Error in expression")
			raise DeclarationError("Invalid expression at {}\n{}".format(node.start_mark, e))


	def _construct_scalar(self, loader: yaml.Loader, node: yaml.Node):

		location = node.start_mark
		if self.Identifier is not None:
			# https://github.com/yaml/pyyaml/blob/4c2e993321ad29a02a61c4818f3cef9229219003/lib3/yaml/reader.py
			location = location.replace("<unicode string>", str(self.Identifier))

		if isinstance(node, yaml.ScalarNode):
			# Value variant e.g.: `!!si 64`
			outlet_type = node.tag.rsplit(':', 1)[1]
			if outlet_type == 'str':
				return node.value
			elif outlet_type[0] in ('u', 's'):
				value = int(node.value)
			elif outlet_type[0] == 'f':
				value = float(node.value)
			else:
				raise NotImplementedError("Unsupport scalar type '{}'".format(outlet_type))
			obj = VALUE(self.App, value=value, outlet_type=outlet_type)


		elif isinstance(node, yaml.MappingNode):
			# Casting variant
			outlet_type = node.tag.rsplit(':', 1)[1]
			value = loader.construct_mapping(node)
			obj = CAST(self.App, arg_what=value['what'], arg_type=outlet_type)

		else:
			NotImplementedError("Unimplemented for YAML node '{}'".format(node))

		obj.set_location(location)
		obj.Node = node
		return obj
