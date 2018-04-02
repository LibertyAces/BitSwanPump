import asyncio
from ..abc.source import Source


class InternalSource(Source):

	'''
See TeeProcessor for details.
	'''

	ConfigDefaults = {
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self._queue = asyncio.Queue() #TODO: Max size (etc.)
		self._started = True
		self._future = None


	def put_nowait(self, event):
		self._queue.put_nowait(event)


	async def start(self):
		self._future = asyncio.ensure_future(self._consume())


	async def _consume(self):

		while self._started:
			event = await self._queue.get()
			if event is None:
				break

			self.process(event)
