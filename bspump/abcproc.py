import abc

class ProcessorBase(abc.ABC):

	def __init__(self, app, pipeline):
		pass

	@abc.abstractmethod
	def process(self, data):
		pass


class Source(abc.ABC):

	def __init__(self, app, pipeline):
		self.Processors = []

	def _append_processor(self, processor):
		self.Processors.append(processor)

	def process(self, data):
		for processor in self.Processors:
			data = processor.process(data)
		if data is not None:
			raise RuntimeError("Incomplete pipeline, data are not consumed by Sink")

	@abc.abstractmethod
	async def start(self):
		pass


class Processor(ProcessorBase):
	pass


class Sink(ProcessorBase):
	pass
