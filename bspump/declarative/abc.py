import logging
import functools
import itertools

from .declerror import DeclarationError

from .typesystem import Outlet

#

L = logging.getLogger(__name__)

#

_IdGenerator = itertools.count(1)


class Expression(object):

	Category = 'Others'


	def __init__(self, app, outlet=None):
		self.Id = '{}.F{}'.format(self.__class__.__name__, next(_IdGenerator))
		self.App = app
		self.Location = None
		self.Node = None  # The YAML node, assigned by a builder during YAML parsing

		if outlet is not None:
			self.Outlet = outlet
		else:
			self.Outlet = Outlet()

		self.Inlets = []


	def initialize(self):
		"""
		Initialize the expression after the syntax tree was build.
		"""
		return


	def __call__(self, context, event, *args, **kwargs):
		raise RuntimeError("Call of the abstract method")


	def optimize(self):
		return None


	def set_location(self, location):
		self.Location = location

	def get_location(self):
		return self.Location


	def walk(self, parent=None, inlet_name=None):
		'''
		Walk the expression tree using Inlets

		`parent` is Expression object
		`inlet_name` is string or integer with the name of the inlet
		'''

		yield (parent, inlet_name, self)

		for child_inlet_name in self.Inlets:

			# Locate inlet in the Expression
			child_inlet = getattr(self, child_inlet_name)

			# Inlet has to be Expression
			assert(isinstance(child_inlet, Expression))

			# Perform the walk
			for x in child_inlet.walk(self, child_inlet_name):
				yield x


	def get_outlet_type(self):
		if self.Outlet is None or self.Outlet.Type is None:
			raise DeclarationError("Failed to resolve type", location=self.Location)
		return self.Outlet.Type


class SequenceExpression(Expression):
	'''
	Convenient class that fits onto SequenceNode from Yaml.

	Example of __call__() method implementation.

	def __call__(self, context, event, *args, **kwargs):
		return functools.reduce(
			lambda x, y: evaluate(x, context, event, *args, **kwargs) + evaluate(y, context, event, *args, **kwargs),
			self.Items
		)
	'''

	def __init__(self, app, *, sequence):
		super().__init__(app)
		self.Items = []
		self.Inlets = []

		for n, item in enumerate(sequence):
			if isinstance(item, Expression):
				self.Items.append(item)

			else:
				assert isinstance(item, (int, str, float, bytes, bool, tuple, list, dict)) or item is None

				from .expression import VALUE
				self.Items.append(
					VALUE(app, value=item)
				)

			self.Inlets.append(n)


	def reduce(self, operator, context, event, *args, **kwargs):
		iterator = [evaluate(item, context, event, *args, **kwargs) for item in self.Items]
		return functools.reduce(operator, iterator)


	def walk(self, parent: Expression = None, inlet_name=None):
		'''
		Walk the expression tree using Inlets

		`parent` is Expression object
		`inlet_name` is an integer with the "name" of the inlet (aka position in `.Items` array)
		'''

		yield(parent, inlet_name, self)

		for child_inlet_name, child_inlet in enumerate(self.Items):
			assert(isinstance(child_inlet, Expression))
			for x in child_inlet.walk(self, child_inlet_name):
				yield x


def evaluate(value, context, event, *args, **kwargs):
	'''
	This is OBSOLETED method and will be removed.
	DO NOT USE IT!
	'''
	try:
		return value(context, event, *args, **kwargs)
	except Exception as e:
		raise DeclarationError(original_exception=e, location=value.get_location())
