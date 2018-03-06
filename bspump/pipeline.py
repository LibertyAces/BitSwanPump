import abc
import asab
from .abcproc import Source

class Pipeline(abc.ABC):


	def __init__(self, app, pipeline_id):

		self.Id = pipeline_id

		# List of processors
		self.Source = None

		# Publish-Subscribe for this pipeline
		self.PubSub = asab.PubSub(app)

		self.State = 'y' # 'r' .. red, 'y' .. yellow, 'g' .. green

		self.Config = None # TODO ...


	# Pipeline construction

	def set_source(self, source):
		"""
		Must be called first in construction phase
		"""
		assert(self.Source is None)
		assert(isinstance(source, Source))
		self.Source = source


	def append_processor(self, processor):
		"""
		Must be called after set_source, last processor has to be sink
		"""
		assert(self.Source is not None)
		#TODO: Check if possible: self.Processors[-1] is Sink, no processors after Sink, ...
		#TODO: Check if fitting
		self.Source._append_processor(processor)


	def construct(self, source, *processors):
		self.set_source(source)
		for processor in processors:
			self.append_processor(processor)


	# Stream processing

	async def start(self):
		return await self.Source.start()

