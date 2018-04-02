import abc
from .config import ConfigObject

class ProcessorBase(abc.ABC, ConfigObject):


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__("pipeline:{}:{}".format(pipeline.Id, id if id is not None else self.__class__.__name__), config=config)

		self.Id = id if id is not None else self.__class__.__name__
		self.Pipeline = pipeline


	@abc.abstractmethod
	def process(self, event):
		raise NotImplemented()


	def start(self):
		'''
		Override this to handle request to start
		'''
		pass


	def flush(self):
		'''
		Override this to handle request to flush all buffers
		'''
		pass

class Processor(ProcessorBase):
	pass
