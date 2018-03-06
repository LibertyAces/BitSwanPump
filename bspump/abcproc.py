import abc

class ProcessorBase(abc.ABC):

	def __init__(self, app, pipeline):
		pass

	@abc.abstractmethod
	def on_consume(self, data):
		pass


class Source(abc.ABC):

	def __init__(self, app, pipeline):
		pass

	@abc.abstractmethod
	async def get(self):
		pass


class Processor(ProcessorBase):
	pass


class Sink(ProcessorBase):
	pass
