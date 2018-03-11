import logging
import abc
from .abc.config import ConfigObject

#

L = logging.getLogger(__name__)

#

class ProcessorBase(abc.ABC, ConfigObject):

	def __init__(self, app, pipeline, id=None):
		super().__init__("pipeline:{}:{}".format(pipeline.Id, id if id is not None else self.__class__.__name__))

		self.Id = id
		self.Pipeline = pipeline

	@abc.abstractmethod
	def process(self, event):
		raise NotImplemented()


class Source(abc.ABC, ConfigObject):

	def __init__(self, app, pipeline, id=None):
		super().__init__("pipeline:{}:{}".format(pipeline.Id, id if id is not None else self.__class__.__name__))

		self.Id = id
		self.Pipeline = pipeline

	def process(self, event):
		self.Pipeline.Metrics.add("pipeline.{}.event_processed".format(self.Pipeline.Id))

		for processor in self.Pipeline.Processors:
			event = processor.process(event)

		if event is not None:
			raise RuntimeError("Incomplete pipeline, event is not consumed by Sink")

	@abc.abstractmethod
	async def start(self):
		raise NotImplemented()


class Processor(ProcessorBase):
	pass


class Sink(ProcessorBase):
	pass
