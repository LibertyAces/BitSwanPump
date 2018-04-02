import abc
import logging
import asyncio
from .config import ConfigObject

#

L = logging.getLogger(__name__)

#

class Source(abc.ABC, ConfigObject):

	'''
Each source represent a coroutine/Future/Task that is running in the context of the main loop.
The coroutine method main() contains an implementation of each particular source.

Source MUST await a pipeline ready state prior producing the event.
It is acomplished by `await self.Pipeline.ready()` call.
	'''

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__("pipeline:{}:{}".format(pipeline.Id, id if id is not None else self.__class__.__name__), config=config)

		self.Id = id if id is not None else self.__class__.__name__
		self.Pipeline = pipeline

		self.MainCoro = None # Contains a main coroutine `main()` if Pipeline is started


	def process(self, event):
		'''
		This method is used to emit event into a pipeline.
		It is synchronous function.
		If the pipeline is not ready, the error is thrown.
		Call `await self.Pipeline.ready()` prior processing the event.
		'''
		if not self.Pipeline._ready.is_set():
			raise RuntimeError("Pipeline is not ready to process events")
		return self.Pipeline.process(event)


	def start(self, loop):
		if self.MainCoro is not None: return
		self.MainCoro = asyncio.ensure_future(self.main(), loop=loop)


	async def stop(self):
		if self.MainCoro is None: return # Source is not started
		self.MainCoro.cancel()
		await self.MainCoro
		if not self.MainCoro.done():
			L.warning("Source '{}' refused to stop: {}".format(self.Id, self.MainCoro))


	@abc.abstractmethod
	async def main(self):
		raise NotImplemented()


	async def stopped(self):
		'''
		Helper that simplyfies the implementation of sources:

		async def main(self):
			... initialize resources here

			await self.stopped()

			... finalize resources here
		'''
		try:
			while True:
				await asyncio.sleep(60)

		except asyncio.CancelledError:
			pass
