import logging
import asyncio
import copy
from ..abc.processor import Processor
from ..abc.source import Source

#

L = logging.getLogger(__name__)

#

class TeeSource(Source):

	'''

class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.socket.TCPStreamSource(app, self, config={'port': 7000}),
			bspump.common.TeeProcessor(app, self, "SampleTeePipeline.*TeeSource"),
			bspump.common.PPrintSink(app, self)
		)


class SampleTeePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.common.TeeSource(app, self),
			bspump.common.PPrintSink(app, self)
		)

	'''

	ConfigDefaults = {
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Loop = app.Loop 
		self.Queue = asyncio.Queue(loop=self.Loop) #TODO: Max size (etc.)


	def put_nowait(self, event):
		self.Queue.put_nowait(event)


	async def main(self):
		try:

			while 1:
				await self.Pipeline.ready()
				event = await self.Queue.get()
				self.process(event)

		except asyncio.CancelledError:
			if self.Queue.qsize() > 0:
				L.warning("Internal source '{}' stopped with {} events in a queue".format(self.Id, self.Queue.qsize()))

#

class TeeProcessor(Processor):

	'''
	See TeeSink for details.
	'''

	ConfigDefaults = {
	}


	def __init__(self, app, pipeline, target, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Source = None

		self._target = target
		self._svc = app.get_service("bspump.PumpService")


	def process(self, event):
		if self.Source is None:
			source = self._svc.locate(self._target)
			if source is None:
				L.warning("TeeProcessor '{}' cannot find internal source '{}'".format(self.Id, self._target))
				return

			if not isinstance(source, TeeSource):
				L.warning("TeeProcessor '{}' require InternalSource as target, not '{}'".format(self.Id, self._target))
				return

			self.Source = source

		event_copy = copy.deepcopy(event)
		self.Source.put_nowait(event_copy)
		#TODO: Throttle pipeline if queue is getting full & unthrottle when getting empty
		return event
