import abc

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
		super().__init__(None, None, None)		
		self.Items = sequence
