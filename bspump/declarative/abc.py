import abc
import functools


class Expression(abc.ABC):

	def __init__(self, app):
		self.App = app

	@abc.abstractmethod
	def __call__(self, context, event, *args, **kwargs):
		pass

	def evaluate(self, value, context, event, *args, **kwargs):
		if isinstance(value, Expression):
			return value(context, event, *args, **kwargs)
		else:
			return value


class SequenceExpression(Expression):
	'''
	Convenient class that fits onto SequenceNode from Yaml.

	Example of __call__() method implementation.

	def __call__(self, context, event, *args, **kwargs):
		return functools.reduce(
			lambda x, y: self.evaluate(x, context, event, *args, **kwargs) + self.evaluate(y, context, event, *args, **kwargs),
			self.Items
		)
	'''

	def __init__(self, app, *, sequence):
		super().__init__(app)
		self.Items = sequence

	def reduce(self, operator, context, event, *args, **kwargs):
		iterator = [self.evaluate(item, context, event, *args, **kwargs) for item in self.Items]
		return functools.reduce(operator, iterator)
