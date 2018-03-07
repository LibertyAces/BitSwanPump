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
		self.Pipeline.Metrics.add("pipeline.{}.event_processed".format(self.Pipeline.Id))

		for processor in self.Pipeline.Processors:
			event = processor.process(event)

		if event is not None:
			raise RuntimeError("Incomplete pipeline, event is not consumed by Sink")

	@abc.abstractmethod
	async def start(self):
		pass


class Processor(ProcessorBase):
	pass


class Sink(ProcessorBase):
	pass
