import abc
import logging
import asyncio
import concurrent.futures
from asab import ConfigObject


L = logging.getLogger(__name__)


class Source(abc.ABC, ConfigObject):

	"""
Each source represent a coroutine/Future/Task that is running in the context of the main loop.
The coroutine method main() contains an implementation of each particular source.

Source MUST await a pipeline ready state prior producing the event.
It is acomplished by `await self.Pipeline.ready()` call.
	"""

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__("pipeline:{}:{}".format(pipeline.Id, id if id is not None else self.__class__.__name__), config=config)

		self.Id = id if id is not None else self.__class__.__name__
		self.Pipeline = pipeline

		self.Task = None  # Contains a main coroutine `main()` if Pipeline is started


	async def process(self, event, context=None):
		"""
		This method is used to emit event into a pipeline.

		If there is an error in the processing of the event, the pipeline is throttled by setting the error and the exception raised.
		The source should catch this exception and fail gracefully.
		"""
		# TODO: Remove this method completely, each source should call pipeline.process() method directly
		await self.Pipeline.process(event, context=context)


	def start(self, loop):
		if self.Task is not None:
			return

		async def _main():
			# This is to properly handle a lifecycle of the main method
			try:
				await self.main()
			except concurrent.futures.CancelledError:
				pass
			except Exception as e:
				self.Pipeline.set_error(None, None, e)
				L.exception("Exception in the source '{}'".format(self.Id))

		self.Task = asyncio.ensure_future(_main(), loop=loop)


	async def stop(self):
		if self.Task is None:
			return  # Source is not started
		if not self.Task.done():
			self.Task.cancel()
		await self.Task
		if not self.Task.done():
			L.error("Source '{}' refused to stop: {}".format(self.Id, self.Task))
		self.Task = None


	def restart(self, loop):
		if self.Task is not None:
			if self.Task.done():
				self.Task.result()
				self.Task = None
		self.start(loop)


	@abc.abstractmethod
	async def main(self):
		raise NotImplementedError()


	async def stopped(self):
		"""
		Helper that simplyfies the implementation of sources:

.. code:: python

	async def main(self):
		... initialize resources here

		await self.stopped()

		... finalize resources here
	"""

		try:
			while True:
				await asyncio.sleep(60)

		except asyncio.CancelledError:
			pass


	def locate_address(self):
		return "{}.*{}".format(self.Pipeline.Id, self.Id)


	def rest_get(self):
		return {
			"Id": self.Id,
			"Class": self.__class__.__name__
		}


	def __repr__(self):
		return '%s(%r)' % (self.__class__.__name__, self.locate_address())


	@classmethod
	def construct(cls, app, pipeline, definition: dict):
		newid = definition.get('id')
		config = definition.get('config')
		return cls(app, pipeline, id=newid, config=config)


class TriggerSource(Source):

	"""
	This is an abstract source class intended as a base for implementation of 'cyclic' sources such as file readers, SQL extractors etc.
	You need to provide a trigger class and implement cycle() method.

	Trigger source will stop execution, when a pipeline is cancelled (raises concurrent.futures.CancelledError).
	This typically happens when a program wants to quit in reaction to a on the signal.

	You also may overload the main() method to provide additional parameters for a cycle() method.

.. code:: python

	async def main(self):
		async with aiohttp.ClientSession(loop=self.Loop) as session:
			await super().main(session)


	async def cycle(self, session):
		session.get(...)

	"""

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.App = app
		self.Loop = app.Loop

		self.TriggerEvent = asyncio.Event(loop=app.Loop)
		self.TriggerEvent.clear()
		self.Triggers = set()


	def time(self):
		return self.App.time()


	def on(self, trigger):
		"""
		Add trigger
		"""
		trigger.add(self)
		self.Triggers.add(trigger)
		return self


	async def main(self, *args, **kwags):
		while True:
			# Wait for pipeline is ready
			await self.Pipeline.ready()

			# Wait for a trigger
			await self.TriggerEvent.wait()

			# Send begin on a cycle event
			self.Pipeline.PubSub.publish("bspump.pipeline.cycle_begin!", pipeline=self.Pipeline)

			# Execute one cycle
			try:
				await self.cycle(*args, **kwags)

			except concurrent.futures.CancelledError:
				# This happens when Ctrl-C is pressed
				L.warning("Pipeline '{}' processing was cancelled".format(self.Pipeline.Id))

				# Send end of a cycle event
				self.Pipeline.PubSub.publish("bspump.pipeline.cycle_canceled!", pipeline=self.Pipeline)

				break

			except BaseException as e:
				self.Pipeline.set_error(None, None, e)

			# Send end of a cycle event
			self.Pipeline.PubSub.publish("bspump.pipeline.cycle_end!", pipeline=self.Pipeline)

			self.TriggerEvent.clear()
			for trigger in self.Triggers:
				trigger.done(self)


	@abc.abstractmethod
	async def cycle(self, *args, **kwags):
		raise NotImplementedError()

	def rest_get(self):
		result = super().rest_get()
		result.update({
			"triggered": self.TriggerEvent.is_set()
		})
		return result
