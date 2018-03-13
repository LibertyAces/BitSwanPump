import abc
import asab
from .abcproc import Source
from .abc.connection import Connection

class Pipeline(abc.ABC):


	def __init__(self, app, pipeline_id):

		self.Id = pipeline_id

		# List of processors
		self.Source = None
		self.Processors = []

		# Publish-Subscribe for this pipeline
		self.PubSub = asab.PubSub(app)
		self.Metrics = app.Metrics

		self.State = 'y' # 'r' .. red, 'y' .. yellow, 'g' .. green

		self.Config = None # TODO ...


	def get_connection(self, app, connection_id):
		if isinstance(connection_id, Connection): return connection_id
		svc = app.get_service("bspump.PumpService")
		return svc.get_connection(connection_id)


	# Pipeline construction

	def set_source(self, source):
		assert(self.Source is None)
		assert(isinstance(source, Source))
		self.Source = source


	def append_processor(self, processor):
		#TODO: Check if possible: self.Processors[-1] is Sink, no processors after Sink, ...
		#TODO: Check if fitting
		self.Processors.append(processor)


	def build(self, source, *processors):
		self.set_source(source)
		for processor in processors:
			self.append_processor(processor)


	# Stream processing

	async def start(self):
		return await self.Source.start()

