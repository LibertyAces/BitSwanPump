import abc
from .config import ConfigObject

class Source(abc.ABC, ConfigObject):


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__("pipeline:{}:{}".format(pipeline.Id, id if id is not None else self.__class__.__name__), config=config)

		self.Id = id if id is not None else self.__class__.__name__
		self.Pipeline = pipeline


	def process(self, event):
		'''
		This method is used to emit event into a pipeline.
		It is synchronous function.
		'''
		if not self.Pipeline._ready.is_set():
			raise RuntimeError("Pipeline is not ready to process events")
		return self.Pipeline.process(event)


	@abc.abstractmethod
	async def start(self):
		raise NotImplemented()
