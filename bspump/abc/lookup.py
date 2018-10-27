import abc
import collections.abc
import json
import asyncio

import asab

class Lookup(abc.ABC, asab.ConfigObject):


	def __init__(self, app, lookup_id, config=None):
		assert(lookup_id is not None)
		super().__init__("lookup:{}".format(lookup_id), config=config)
		self.Id = lookup_id
		self.PubSub = asab.PubSub(app)


	def ensure_future_update(self, loop):
		return asyncio.ensure_future(self._do_update(), loop=loop)


	async def _do_update(self):
		res = await self.load()
		if res is not False:
			self.PubSub.publish("bspump.Lookup.changed!")


	@abc.abstractmethod
	async def load(self):
		pass


class MappingLookup(Lookup, collections.abc.Mapping):
	pass


class DictionaryLookup(MappingLookup):

	def __init__(self, app, lookup_id, config=None):
		super().__init__(app, lookup_id, config=config)
		self.Dictionary = {}

	def __getitem__(self, key):
		return self.Dictionary.__getitem__(key)

	def __iter__(self):
		return self.Dictionary.__iter__()

	def __len__(self):
		return self.Dictionary.__len__()
