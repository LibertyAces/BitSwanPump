import abc
import asyncio
import types
import logging
import itertools
import asab
from .abcproc import Source, Generator
from .abc.connection import Connection
from .exception import ProcessingError

#

L = logging.getLogger(__name__)

#

class Pipeline(abc.ABC):


	def __init__(self, app, pipeline_id):

		self.Id = pipeline_id
		self.Loop = app.Loop

		self.Sources = []
		self.Processors = [[]] # List of lists of processors, the depth is increased by a Generator object

		# Publish-Subscribe for this pipeline
		self.PubSub = asab.PubSub(app)
		self.Metrics = app.Metrics

		self._error = None # None if not in error state otherwise there is a tuple (exception, event)

		self._throttles = set()

		self._ready = asyncio.Event(loop = app.Loop)
		self._ready.clear()

		# Chillout is used to break a pipeline processing to smaller tasks that allows other event in event loop to be processed
		self._chillout_trigger = 10000
		self._chillout_counter = 0


	def set_error(self, exc, event):
		'''
		If called with `exc is None`, then reset error (aka recovery)
		'''
		if not self.catch_error(exc, event):
			self.Metrics.add("bspump.pipeline.warning.{}".format(self.Id))
			self.PubSub.publish("bspump.pipeline.warning!", pipeline=self)
			return

		self.Metrics.add("bspump.pipeline.error.{}".format(self.Id))

		if exc is None:
			if self._error is not None:
				self._error = None
				self._evaluate_ready()

		else:
			if (self._error is not None):
				L.warning("Error on a pipeline is already set!")
			
			self._error = (exc, event)
			L.warning("Pipeline '{}' stopped due to a processing error: {}".format(self.Id, exc))

			self.PubSub.publish("bspump.pipeline.error!", pipeline=self)
			self._evaluate_ready()


	def catch_error(self, exception, event):
		'''
		Override to evaluate on the pipeline processing error.
		Return True for hard errors (stop the pipeline processing) or False for soft errors that will be ignored 
		'''
		return True


	def throttle(self, who, enable=True):
		L.warning("Throttle: {}".format(enable))
		if enable:
			self._throttles.add(who)
		else:
			self._throttles.remove(who)

		self._evaluate_ready()


	def _evaluate_ready(self):
		orig_ready = self._ready.is_set()

		# Do we observed an error?
		new_ready = self._error is None

		# Are we throttled?
		if new_ready:
			new_ready = len(self._throttles) == 0 

		if orig_ready != new_ready:
			if new_ready:
				self._ready.set()
				self.PubSub.publish("bspump.pipeline.ready!", pipeline=self)
			else:
				self._ready.clear()
				self.PubSub.publish("bspump.pipeline.not_ready!", pipeline=self)


	async def ready(self):
		self._chillout_counter += 1
		if self._chillout_counter == self._chillout_trigger:
			self._chillout_counter = 0
			await asyncio.sleep(0.0001, loop = self.Loop)

		await self._ready.wait()


	def process(self, event, depth=0):
		if depth == 0:
			self.Metrics.add("bspump.pipeline.event_in.{}".format(self.Id))

		for processor in self.Processors[depth]:
			try:
				event = processor.process(event)
			except Exception as e:
				if depth > 0: raise # Handle error on the top level
				L.exception("Pipeline processing error in the '{}' on depth {}".format(self.Id, depth))
				self.set_error(e, event)
				return False

			if event is None: # Event has been consumed on the way
				return True

		if event is None:
			return True

		# If the event is generator and there is more in the processor pipeline, then enumerate generator
		if isinstance(event, types.GeneratorType) and len(self.Processors) > depth:
			for gevent in event:
				self.process(gevent, depth+1)

		else:
			try:
				raise ProcessingError("Incomplete pipeline, event '{}' is not consumed by a Sink".format(event))
			except Exception as e:
				L.exception("Pipeline processing error in the '{}' on depth {}".format(self.__class__.__name__, depth))
				self.set_error(e, event)
				return False

		return True


	def flush(self):
		# Ensure that all buffers etc. are flushed
		for processor in itertools.chain.from_iterable(self.Processors):
			processor.flush()


	def locate_connection(self, app, connection_id):
		if isinstance(connection_id, Connection): return connection_id
		svc = app.get_service("bspump.PumpService")
		connection = svc.locate_connection(connection_id)
		if connection is None:
			raise RuntimeError("Cannot locate connection '{}'".format(connection_id))
		return connection


	# Pipeline construction

	def set_source(self, source):
		if isinstance(source, Source):
			self.Sources.append(source)
		else:
			self.Sources.extend(source)


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
		# Start all sources
		asyncio.gather(*[s.start() for s in self.Sources], loop=self.Loop)
		self._evaluate_ready()
