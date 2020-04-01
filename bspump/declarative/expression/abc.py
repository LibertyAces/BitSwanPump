import abc


class Expression(abc.ABC):

	def __init__(self, expression: dict):
		pass

	@abc.abstractmethod
	def __call__(self, context, event, *args, **kwargs):
		pass
