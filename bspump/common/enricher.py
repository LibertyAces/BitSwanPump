import logging

import asab
import asab.proactor

import bspump

###

L = logging.getLogger(__name__)

###


class OOBLookupEnricher(bspump.Generator):
	"""
	OOBLookupEnricher obtains lookup values on threads. As input,
	it expects a dictionary-based lookup with write-through cache,
	which may take time to load.

	The lookup value is obtained for input_key inside the event
	and stored in output_key attribute.
	"""

	ConfigDefaults = {
		"input_key": "key",
		"output_key": "output",
	}

	def __init__(self, app, pipeline, lookup_id, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		app.add_module(asab.proactor.Module)
		self.ProactorService = app.get_service("asab.ProactorService")

		self.InputKey = str(self.Config["input_key"])
		self.OutputKey = str(self.Config["output_key"])

		svc = app.get_service("bspump.PumpService")
		self.Lookup = svc.locate_lookup(lookup_id)

	async def generate(self, context, event, depth):
		key = event.get(self.InputKey)
		if key is None:
			L.warn("Attribute input_key '{}' not present in the event, skipping lookup.".format(self.InputKey))
			await self.Pipeline.inject(context, event, depth)
			return

		# Obtain the value from the lookup
		# There are two OOB ways (see examples): proactor/threads or asynchronous
		if "get_async" in dir(self.Lookup):
			event[self.OutputKey] = await self.Lookup.get_async(key)
		else:
			event[self.OutputKey] = await self.ProactorService.execute(
				self.process_on_thread,
				key
			)

		await self.Pipeline.inject(context, event, depth)

	def process_on_thread(self, key):
		return self.Lookup.get(key)
