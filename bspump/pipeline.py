import abc
import asab
from .abcproc import Source

class Pipeline(abc.ABC):


	def __init__(self, app, pipeline_id):

		self.id = pipeline_id

		# List of processors
		self.Source = None
		self.Processors = []

		# Publish-Subscribe for this pipeline
		self.PubSub = asab.PubSub(app)

		self.State = 'y' # 'r' .. red, 'y' .. yellow, 'g' .. green

		self.Config = None # TODO ...

		self.construct(app)


	# Pipeline construction

	@abc.abstractmethod
	def construct(self, app):
		pass


	def set_source(self, source):
		assert(self.Source is None)
		assert(isinstance(source, Source))
		self.Source = source


	def append_processor(self, processor):
		#TODO: Check if possible: self.Processors[0] is Source, self.Processors[-1] is Sink, no processors after Sink, ...
		#TODO: Check if fitting
		self.Processors.append(processor)


	# Stream processing

	async def process(self, future):

		while True: #TODO: This is where you need to implement grace finish
			print("Pipeline.process - 1")
			data = await self.Source.get()	
			print("Pipeline.process - 2", data)

			for processor in self.Processors:
				data = processor.on_consume(data)

		future.set_result('xxxx')
