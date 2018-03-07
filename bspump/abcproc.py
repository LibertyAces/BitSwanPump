import abc

class ProcessorBase(abc.ABC):

	def __init__(self, app, pipeline):
		pass

	@abc.abstractmethod
	def process(self, event):
		pass


class Source(abc.ABC):

	def __init__(self, app, pipeline):
		self.Pipeline = pipeline
		

	def process(self, event):
		self.Pipeline.Metrics.add("event.processed")

		for processor in self.Pipeline.Processors:
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
