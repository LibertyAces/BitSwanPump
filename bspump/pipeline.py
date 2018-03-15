import abc
import types
import asab
from .abcproc import Source, Generator
from .abc.connection import Connection

class Pipeline(abc.ABC):


	def __init__(self, app, pipeline_id):

		self.Id = pipeline_id

		# List of processors
		self.Source = None
		self.Processors = [[]] # List of lists of processors, the depth is increased by a Generator object

		# Publish-Subscribe for this pipeline
		self.PubSub = asab.PubSub(app)
		self.Metrics = app.Metrics


	def process(self, event, depth=0):

		self.Metrics.add("pipeline.{}.event_processed".format(self.Id))

		for processor in self.Processors[depth]:
			event = processor.process(event)
			if event is None: # Event has been consumed on the way
				return

		if event is None:
			return

		# If the event is generator and there is more in the processor pipeline, then enumerate generator
		if isinstance(event, types.GeneratorType) and len(self.Processors) > depth:
			for gevent in event:
				self.process(gevent, depth+1)

		else:
			raise RuntimeError("Incomplete pipeline, event `{}` is not consumed by Sink".format(event))


	def locate_connection(self, app, connection_id):
		if isinstance(connection_id, Connection): return connection_id
		svc = app.get_service("bspump.PumpService")
		connection = svc.locate_connection(connection_id)
		if connection is None:
			raise RuntimeError("Cannot locate connection '{}'".format(connection_id))
		return connection


	# Pipeline construction

	def set_source(self, source):
		assert(self.Source is None)
		assert(isinstance(source, Source))
		self.Source = source


	def append_processor(self, processor):
		#TODO: Check if possible: self.Processors[*][-1] is Sink, no processors after Sink, ...
		#TODO: Check if fitting
		self.Processors[-1].append(processor)

		if isinstance(processor, Generator):
			self.Processors.append([])


	def build(self, source, *processors):
		self.set_source(source)
		for processor in processors:
			self.append_processor(processor)


	# Stream processing

	async def start(self):
		return await self.Source.start()

