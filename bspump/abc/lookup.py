import abc
import collections.abc
import json
import asyncio

from asab import ConfigObject

class Lookup(abc.ABC, ConfigObject):


	def __init__(self, app, lookup_id, config=None):
		assert(lookup_id is not None)
		super().__init__("lookup:{}".format(lookup_id), config=config)
		self.Id = lookup_id
		self.LoadTask = asyncio.ensure_future(self.load(), loop=app.Loop)


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
