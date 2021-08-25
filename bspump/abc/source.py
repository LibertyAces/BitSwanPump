import logging
import asyncio
import concurrent.futures
from asab import ConfigObject


L = logging.getLogger(__name__)


class Source(ConfigObject):
	"""
	Source class is responsible for connecting to a source and propagating the events or data from the source to processors.

	"""
	def __init__(self, app, pipeline, id=None, config=None):
		"""
		Set the initial ID, pipeline and Task.

		**Parameters**

		app : Application
			Name of an Application.

		pipeline : address of a pipeline
			Name of a pipeline.

		id : str, default None
			Name of a the Pipeline.

		config : compatible config type , default None
			Option for adding a configuration file.

		"""
		super().__init__("pipeline:{}:{}".format(pipeline.Id, id if id is not None else self.__class__.__name__), config=config)

		self.Id = id if id is not None else self.__class__.__name__
		self.Pipeline = pipeline

		self.Task = None  # Contains a main coroutine `main()` if Pipeline is started


	async def process(self, event, context=None):
		"""
		This method is used to emit event into a :meth:`Pipeline <bspump.Pipeline()>`.

		**Parameters**

		event: Data with time stamp stored in any data type, usually JSON.
			Message or information that is passed to the method and emitted into a pipeline.

		context : default None
			Additional information.

		If there is an error in the processing of the event, the :meth:`Pipeline <bspump.Pipeline()>` is throttled by setting the error and the exception raised.

		:hint The source should catch this exception and fail gracefully.

		"""
		# TODO: Remove this method completely, each source should call pipeline.process() method directly
		await self.Pipeline.process(event, context=context)


	def start(self, loop):
		"""
		Start the pipeline through the _main method, but if main method is implemented
		it starts the coroutine using main method instead.

		**Parameters**

		loop : ?
			Contains the coroutines.


		"""
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

		self.Task = loop.create_task(_main())


	async def stop(self):
		"""
		Stop the Source using self.Task. If the processes are not done it cancels them or raises an error.

		"""
		if self.Task is None:
			return  # Source is not started
		if not self.Task.done():
			self.Task.cancel()
		await self.Task
		if not self.Task.done():
			L.error("Source '{}' refused to stop: {}".format(self.Id, self.Task))
		self.Task = None


	def restart(self, loop):
		"""
		Restart the loop of coroutines and returns result() method.

		**Parameters**

		loop : ??
			Contains the coroutines.

		"""
		if self.Task is not None:
			if self.Task.done():
				self.Task.result()
				self.Task = None
		self.start(loop)


	async def main(self):
		"""
		Can be implemented for additional features, else will raise NotImplementedError and _main is called instead.

		"""
		raise NotImplementedError()


	async def stopped(self):
		"""
		Wait for all asynchronous tasks to be completed. It is helper that simplifies the implementation of sources.

		Example:

		..code:: python

			async def main(self):
				#... initialize resources here

				await self.stopped()
				#... finalize resources here

		"""

		try:
			while True:
				await asyncio.sleep(60)

		except asyncio.CancelledError:
			pass


	def locate_address(self):
		"""
		locates address of a pipeline

		:return: ID and ID of a Pipeline as a string

		"""
		return "{}.*{}".format(self.Pipeline.Id, self.Id)


	def rest_get(self):
		"""

		:return: ID and class ID

		"""
		return {
			"Id": self.Id,
			"Class": self.__class__.__name__
		}


	def __repr__(self):
		return '%s(%r)' % (self.__class__.__name__, self.locate_address())


	@classmethod
	def construct(cls, app, pipeline, definition: dict):
		"""
		can create a source based on a specific definition. For example, a JSON file.

		**Parameters**

		app : Application
			ID of the app

		pipeline : Pipeline
			specification of a pipeline

		definition : dict
			definition that is used to create a source


		:return: cls(app, newid, config)

		"""
		newid = definition.get('id')
		config = definition.get('config')
		args = definition.get('args')
		if args is not None:
			return cls(app, pipeline, id=newid, config=config, **args)
		else:
			return cls(app, pipeline, id=newid, config=config)


class TriggerSource(Source):

	"""
	Description:

	|

	"""

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.App = app
		self.Loop = app.Loop

		self.TriggerEvent = asyncio.Event(loop=app.Loop)
		self.TriggerEvent.clear()
		self.Triggers = set()


	def time(self):
		"""
		Method used for measuring an accurate time.

		:return: App.time()

		"""
		return self.App.time()


	def on(self, trigger):
		"""
		sets a Trigger which is a method that waits for a given condition

		**Parameters**

		trigger : keyword of a trigger
			Given condition that

		:return: Trigger.add(trigger)                                                                        a

		"""
		trigger.add(self)
		self.Triggers.add(trigger)
		return self


	async def main(self, *args, **kwags):
		"""
		Waits for pipeline, triggers and calls exceptions when the source is initiated

		**Parameters**

		*args : ?

		**kwags : ?

		|

		"""
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


	async def cycle(self, *args, **kwags):
		"""
		Not implemented

		**Parameters**

		*args : ?

		**kwags : ?


		"""
		raise NotImplementedError()


	def rest_get(self):
		result = super().rest_get()
		result.update({
			"triggered": self.TriggerEvent.is_set()
		})
		return result
