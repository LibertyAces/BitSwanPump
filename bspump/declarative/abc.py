import logging
import functools
import itertools

from .declerror import DeclarationError

#

L = logging.getLogger(__name__)

#

_IdGenerator = itertools.count(1)


class Expression(object):

	Attributes = None  # Must be a list, if missing, then the Expression class is not complete

	def __init__(self, app):
		if self.Attributes is None:
			raise NotImplementedError("Missing 'Attributes' in {}".format(self))

		self.Id = 'E{}'.format(next(_IdGenerator))
		self.App = app
		self.Location = None
		self.Node = None  # The YAML node, assigned by a builder during YAML parsing

	def __call__(self, context, event, *args, **kwargs):
		raise RuntimeError("Call of the abstract method")

	def set_location(self, location):
		self.Location = location

	def get_location(self):
		return self.Location

	def optimize(self):
		return None

	def walk(self, parent=None, key=None):
		'''
		key in the Expression is the string, which is a name of the attribute with the child expression
		'''

		yield (parent, key, self)

		for key in self.Attributes:
			v = getattr(self, key, None)
			if isinstance(v, Expression):
				for x in v.walk(self, key):
					yield x
			else:
				yield (self, key, v)

	def set(self, key, value):
		setattr(self, key, value)

	def get_outlet_type(self):
		return '???'

	def consult_inlet_type(self, key, child):
		raise NotImplementedError("Parent consultation at '{}'".format(self))


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

	Attributes = {
		"Items": []
	}

	def __init__(self, app, *, sequence):
		super().__init__(app)
		self.Items = []

		for i in sequence:
			if isinstance(i, Expression):
				self.Items.append(i)

			else:
				assert isinstance(i, (int, str, float, bytes, bool, tuple, list, dict)) or i is None

				# So far used in the WHEN expression
				if isinstance(i, dict):
					continue

				from .expression import VALUE
				self.Items.append(
					VALUE(app, value=i)
				)


	def reduce(self, operator, context, event, *args, **kwargs):
		iterator = [evaluate(item, context, event, *args, **kwargs) for item in self.Items]
		return functools.reduce(operator, iterator)


	def walk(self, parent=None, key=None):
		'''
		key in the Sequence expression is the integer, which is a position in self.Items list
		'''
		yield(parent, key, self)

		for key, i in enumerate(self.Items):
			if isinstance(i, Expression):
				for x in i.walk(self, key):
					yield x
			else:
				raise NotImplementedError(":-(")


	def set(self, key, value):
		self.Items[key] = value


	def get_items_inlet_type(self):
		'''
		This method evaluate the inlet type for `Items` sequence
		'''
		return '?'


def evaluate(value, context, event, *args, **kwargs):
	try:
		return value(context, event, *args, **kwargs)
	except Exception as e:
		raise DeclarationError(original_exception=e, location=value.get_location())
