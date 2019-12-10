import logging
from .routing import InternalSource, RouterProcessor


L = logging.getLogger(__name__)


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

			processor.bind(self.locate_address())
			unbind_processor.append(processor)

		try:
			await super().main()
		finally:
			for processor in unbind_processor:
				processor.unbind(self.locate_address())


#

class TeeProcessor(RouterProcessor):

	'''
	See TeeSource for details.
	'''

	ConfigDefaults = {
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Targets = []


	def bind(self, target: str):
		'''
		Target is a bspump.PumpService.locate() string
		'''
		self.Targets.append(target)
		return self


	def unbind(self, target: str):
		self.Targets.remove(target)
		self.unlocate(target)
		return self


	def process(self, context, event):
		for source in self.Targets:
			self.route(context, event, source)
		return event
