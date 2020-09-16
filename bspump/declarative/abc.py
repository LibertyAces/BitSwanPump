import abc
import functools
import logging

from .declerror import DeclarationError

#

L = logging.getLogger(__name__)

#


class Expression(abc.ABC):

	def __init__(self, app=None):
		self.App = app
		self.Location = None
		self.Node = None  # The YAML node, assigned by a builder during YAML parsing

	@abc.abstractmethod
	def __call__(self, context, event, *args, **kwargs):
		pass

	def set_location(self, location):
		self.Location = location

	def get_location(self):
		return self.Location


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
		self.Items = sequence

	def reduce(self, operator, context, event, *args, **kwargs):
		iterator = [evaluate(item, context, event, *args, **kwargs) for item in self.Items]
		return functools.reduce(operator, iterator)


def evaluate(value, context, event, *args, **kwargs):
	try:
		if isinstance(value, Expression):
			return value(context, event, *args, **kwargs)
		else:
			return value
	except Exception as e:
		raise DeclarationError(original_exception=e, location=value.get_location())
