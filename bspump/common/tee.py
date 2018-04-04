import logging
import asyncio
import copy
from ..abc.processor import Processor
from ..abc.source import Source

#

L = logging.getLogger(__name__)

#

class InternalSource(Source):


	ConfigDefaults = {
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Loop = app.Loop 
		self.Queue = asyncio.Queue(loop=self.Loop) #TODO: Max size (etc.)


	def put(self, event):
		self.Queue.put_nowait(event)


	async def main(self):
		try:

			while 1:
				await self.Pipeline.ready()
				event = await self.Queue.get()
				self.process(event)

		except asyncio.CancelledError:
			if self.Queue.qsize() > 0:
				L.warning("Source '{}' stopped with {} events in a queue".format(self.Id, self.Queue.qsize()))

#

class TeeSource(InternalSource):

	'''

class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.socket.TCPStreamSource(app, self, config={'port': 7000}),
			bspump.common.TeeProcessor(app, self).bind("SampleTeePipeline.*TeeSource"),
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

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Targets = []
		self._svc = app.get_service("bspump.PumpService")


	def bind(self, target):
		self.Targets.append(target)
		return self


	async def main(self):

		unbind_processor = []
		for target in self.Targets:
			processor = self._svc.locate(target)
			if processor is None:
				L.warning("TeeSource '{}' cannot find processor '{}'".format(self.Id, target))
				return

			if not isinstance(processor, TeeProcessor):
				L.warning("TeeSource '{}' requires TeeProcessor as target, not '{}'".format(self.Id, target))
				return

			processor.bind(self)
			unbind_processor.append(processor)

		try:
			await super().main()
		finally:
			for processor in unbind_processor:
				processor.unbind(self)


#

class TeeProcessor(Processor):

	'''
	See TeeSink for details.
	'''

	ConfigDefaults = {
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Sources = None
		self.Targets = []

		self._svc = app.get_service("bspump.PumpService")


	def bind(self, target):
		'''
		Target can be a bspump.PumpService.locate() string or an instance of TeeSource object.
		'''
		self.Sources = None # Trigger location of the target sources
		self.Targets.append(target)
		return self


	def unbind(self, target):
		self.Sources = None # Trigger location of the target sources
		self.Targets.remove(target)
		return self


	def process(self, event):
		if self.Sources is None:
			self.Sources = []
			for target in self.Targets:
				if isinstance(target, TeeSource):
					# If we received direct reference to a target source, use that
					source = target
				else:
					source = self._svc.locate(target)
					if source is None:
						L.warning("TeeProcessor '{}' cannot find source '{}'".format(self.Id, target))
						return
					if not isinstance(source, TeeSource):
						L.warning("TeeProcessor '{}' requires TeeSource as target, not '{}'".format(self.Id, target))
						return

				self.Sources.append(source)

		#TODO: Throttle pipeline if queue is getting full & unthrottle when getting empty
		for source in self.Sources:
			event_copy = copy.deepcopy(event)
			source.put(event_copy)

		return event
