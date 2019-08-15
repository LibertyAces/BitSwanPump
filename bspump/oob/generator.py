import abc

import asyncio

from ..abc.generator import Generator


class OOBGenerator(Generator):
	"""
    OOBGenerator processes originally synchronous events "out-of-band" e.g. out of the synchronous processing within the pipeline.

    Specific implementation of OOBGenerator should implement the process_oob method to process events while performing long running (asynchronous) tasks such as HTTP requests.
    The long running tasks may enrich events with relevant information, such as output of external calculations.

    Example of process_oob method:

        async def process_oob(self, context, event):

            async with aiohttp.ClientSession() as session:
                async with session.get("https://example.com/resolve_color/{}".format(event.get("color_id", "unknown"))) as resp:
                    if resp.status != 200:
                        return event
                color = await resp.json()
                event["color"] = color

            return event

"""

	ConfigDefaults = {
		"queue_max_size": 100,
		"num_of_workers": 10,
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)

		self.IsStarted = True

		self._queue_max_size = int(self.Config["queue_max_size"])
		self._queue = asyncio.Queue(loop=self.Loop)
		self.App.PubSub.subscribe("Application.exit!", self._on_exit)

		# Register workers
		self._workers_size = int(self.Config["num_of_workers"])
		self._workers_pool = []
		for i in range(0, self._workers_size):
			future = asyncio.ensure_future(self._worker(), loop=self.Loop)
			self._workers_pool.append(future)

		# Metrics
		metrics_service = self.App.get_service('asab.MetricsService')
		self.eventStatsCounter = metrics_service.create_counter(
			"oobgenerator.stats",
			tags={},
			init_values={
				'event.drop': 0,
				'event.in': 0,
				'event.out': 0,
			}
		)

	async def _worker(self):
		while True:

			if not self.IsStarted and self._queue.qsize() == 0:
				break

			context_event = await self._queue.get()
			context = context_event[0]
			event = context_event[1]
			depth = context_event[2]
			if event is None:
				break

			output_event = await self.process_oob(context, event)
			if output_event is not None:
				await self.Pipeline.inject(context, output_event, depth + 1)
				self.eventStatsCounter.add("event.out", 1)
			else:
				self.eventStatsCounter.add("event.drop", 1)

			await asyncio.sleep(0.01)


	async def _on_exit(self, event_name):
		self.IsStarted = False

		for i in range(0, self._workers_size):
			self._queue.put_nowait(None)

		pending = self._workers_pool
		while len(pending) > 0:
			done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)


	def process(self, context, event):
		self.Pipeline.ensure_generator_future(
			self.generate(context, event, self.PipelineDepth)
		)
		self.eventStatsCounter.add("event.in", 1)
		return None


	async def generate(self, context, event, depth):
		while self._queue.qsize() == self._queue_max_size:
			await asyncio.sleep(0.01)
		self._queue.put_nowait([context, event, depth])


	@abc.abstractmethod
	async def process_oob(self, context, event):
		raise NotImplemented()
