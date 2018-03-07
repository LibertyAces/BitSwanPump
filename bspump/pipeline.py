import abc
import asab
from .abcproc import Source

class Pipeline(abc.ABC):


	def __init__(self, app, pipeline_id):

		self.Id = pipeline_id

		# List of processors
		self.Source = None
		self.Processors = []

		# Publish-Subscribe for this pipeline
		self.PubSub = asab.PubSub(app)
		self.Metrics = asab.Metrics(app)

		self.State = 'y' # 'r' .. red, 'y' .. yellow, 'g' .. green

		self.Config = None # TODO ...


	# Pipeline construction

	def set_source(self, source):
		assert(self.Source is None)
		assert(isinstance(source, Source))
		self.Source = source


	def append_processor(self, processor):
		#TODO: Check if possible: self.Processors[-1] is Sink, no processors after Sink, ...
		#TODO: Check if fitting
		self.Processors.append(processor)


	def construct(self, source, *processors):
		self.set_source(source)
		for processor in processors:
			self.append_processor(processor)


	# Stream processing

	async def start(self):
		return await self.Source.start()

