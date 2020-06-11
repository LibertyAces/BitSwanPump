import abc
import functools


class Expression(abc.ABC):

	def __init__(self, app):
		self.App = app
		self.Node = None  # The YAML node, assigned by a builder during YAML parsing

	@abc.abstractmethod
	def __call__(self, context, event, *args, **kwargs):
		pass


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


def evaluate(self, value, context, event, *args, **kwargs):
	if isinstance(value, Expression):
		return value(context, event, *args, **kwargs)
	else:
		return value
