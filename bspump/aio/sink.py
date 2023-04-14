import logging
import asyncio

from ..abc.sink import Sink

#

L = logging.getLogger(__name__)

#


class AsyncSink(Sink):
	"""
	Inherit from the sink and override the `consume` coroutine:

	class MySink(bspump.aio.AsyncSink):

		async def consume(self, context, event):
			...
	"""

	ConfigDefaults = {
		"output_queue_max_size": 100,
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)

		self.Queue = asyncio.Queue()
		self.QueueMaxSize = int(self.Config["output_queue_max_size"])
		assert (self.QueueMaxSize >= 1)

		self.Task = asyncio.ensure_future(
			self._task()
		)

		self.Exiting = False

		app.PubSub.subscribe("Application.exit!", self._on_exit)


	async def _task(self):

		while not self.Exiting:

			try:
				context, event = await self.Queue.get()

				# Unthrottle if needed
				if self.Queue.qsize() == (self.QueueMaxSize - 1):
					self.Pipeline.throttle(self.Queue, False)

				# Consume the event
				await self.consume(context, event)

			except Exception as e:
				L.exception("The following exception occurred in async sink: '{}'".format(e))


	async def _on_exit(self, event_name):
		self.Exiting = True

		if self.Task is not None:
			t = self.Task
			self.Task = None
			await t


	def process(self, context, event):
		self.Queue.put_nowait((context, event))

		if self.Queue.qsize() == self.QueueMaxSize:
			self.Pipeline.throttle(self.Queue, True)


	async def consume(self, context, event):
		"""
		Method to be overridden.
		"""
		pass
