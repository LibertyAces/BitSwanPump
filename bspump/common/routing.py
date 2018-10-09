import logging
import asyncio
import copy
from ..abc.source import Source
from ..abc.sink import Sink

#

L = logging.getLogger(__name__)

#

class InternalSource(Source):


	ConfigDefaults = {
		'queue_max_size': 10,
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Loop = app.Loop 
		self.Queue = asyncio.Queue(maxsize=int(self.Config.get('queue_max_size')), loop=self.Loop)


	def put(self, context, event):
		'''
		Context can be empty dictionary if is not provided
		'''

		self.Queue.put_nowait((
			copy.deepcopy(context),
			copy.deepcopy(event)
		))


	async def main(self):
		try:

			while True:
				await self.Pipeline.ready()
				context, event = await self.Queue.get()
				await self.process(event, context={'ancestor':context})

		except asyncio.CancelledError:
			if self.Queue.qsize() > 0:
				L.warning("Source '{}' stopped with {} events in a queue".format(self.Id, self.Queue.qsize()))


	def rest_get(self):
		rest = super().rest_get()
		rest['Queue'] = self.Queue.qsize()
		return rest

#

class RouterSink(Sink):

	'''
	Abstract Sink that dispatches events to other internal sources.
	One should override the process() method and call dispatch() with target source id.
	'''


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		self.ServiceBSPump = app.get_service("bspump.PumpService")
		self.SourcesCache = {}


	def dispatch(self, context, event, source_id):
		source = self.SourcesCache.get(source_id)
		
		if source is None:
			source = self.ServiceBSPump.locate(source_id)
			if source is None:
				L.warning("Cannot locate '{}' in '{}'".format(source_id, self.Id))
				raise RuntimeError("Cannot locate '{}' in '{}'".format(source_id, self.Id))
			self.SourcesCache[source_id] = source

		source.put(context, event)
