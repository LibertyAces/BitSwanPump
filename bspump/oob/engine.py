import asyncio

import asab


class OOBEEngine(object):
	"""
	OOBEEngine processes originally synchronous events asynchronously.
	Specific implementation of OOBEEngine should override the process method.

		async def process(self, context, event):
			pass

	"""

	asab.Config.add_defaults({
		"OOBEEngine": {
			"queue_max_size": 100,
			"num_of_workers": 10,
		}
	})

	def __init__(self, app, destination):
		super().__init__()

		self._started = True

		self.App = app
		self.DestinationSource = destination

		self.Context = None

		self._queue_max_size = int(asab.Config["OOBEEngine"]["queue_max_size"])
		self._queue = asyncio.Queue(loop=self.App.Loop)
		self.App.PubSub.subscribe("Application.exit!", self._on_exit)

		# Register workers
		self._workers_size = int(asab.Config["OOBEEngine"]["num_of_workers"])
		self._workers_pool = []
		for i in range(0, self._workers_size):
			future = asyncio.ensure_future(self._worker(), loop=self.App.Loop)
			self._workers_pool.append(future)

		# Metrics
		metrics_service = self.App.get_service('asab.MetricsService')
		self.eventStatsCounter = metrics_service.create_counter(
			"oobeengine.stats",
			tags={},
			init_values={
				'event.drop': 0,
				'event.in': 0,
				'event.out': 0,
			}
		)


	def put(self, context, event):
		if self.Context is None:
			self.Context = context

		if event is None:
			return

		self._queue.put_nowait(event)
		self.eventStatsCounter.add("event.in", 1)

		if self._queue.qsize() == self._queue_max_size:
			self.App.PubSub.publish("OOBEEngine.pause!", self)


	async def _worker(self):
		while True:

			if not self._started and self._queue.qsize() == 0:
				break

			input_event = await self._queue.get()
			if input_event is None:
				break

			if self._queue.qsize() == self._queue_max_size - 1:
				self.App.PubSub.publish("OOBEEngine.unpause!", self, asynchronously=True)

			output_event = await self.process(self.Context, input_event)
			if output_event is not None:
				await self.DestinationSource.put_async(self.Context, output_event)
				self.eventStatsCounter.add("event.out", 1)
			else:
				self.eventStatsCounter.add("event.drop", 1)

			await asyncio.sleep(1)


	async def _on_exit(self, event_name):
		self._started = False

		for i in range(0, self._workers_size):
			self._queue.put_nowait(None)

		pending = self._workers_pool
		while len(pending) > 0:
			done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)


	async def process(self, context, event):
		pass
