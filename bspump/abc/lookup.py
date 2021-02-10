import asyncio
import collections.abc
import json
import logging
import os
import struct

import asab

import provider

###

L = logging.getLogger(__name__)

###


class Lookup(asab.ConfigObject):
	"""
	Lookups serve for fast data searching in lists of key-value type. They can subsequently be localized and used
	in pipeline objects (processors and the like). Each lookup requires a statically or dynamically created value list.

	If the "lazy" parameter in the constructor is set to True, no load method is called and the user is expected
	to call it when necessary.
	"""


	ConfigDefaults = {
		"master_url": "",  # If not empty, a lookup is in slave mode (will load data from master or cache)
		"master_lookup_id": "",  # If not empty, it specify the lookup id that will be used for loading from master
		"master_timeout": 30,  # In secs.
		"master_url_endpoint": "",
	}

	def __init__(self, app, id=None, config=None, lazy=False):
		_id = id if id is not None else self.__class__.__name__
		super().__init__("lookup:{}".format(_id), config=config)
		self.Id = _id
		self.App = app
		self.Loop = app.Loop
		self.Lazy = lazy
		self.IsLoaded = False

		self.PubSub = asab.PubSub(app)

		self.ETag = None  # TODO: is this necessary?
		self.MasterURL = None
		self.Provider = None
		self.Cache = None

		url = self.Config.get("master_url", "").strip()
		self._create_provider(url)

		cache_path = os.path.join(
			os.path.abspath(asab.Config["general"]["var_dir"]),  # TODO: should be configurable?
			"lookup_{}.cache".format(self.Id)
		)
		self.Cache = provider.FileSystemProvider(self.App, cache_path)

		master_url = self.Config.get("master_url", None)
		if master_url is not None:
			while master_url[-1] == '/':
				master_url = master_url[:-1]
			master_lookup_id = self.Config['master_lookup_id']
			if master_lookup_id == "":
				master_lookup_id = self.Id
			self.MasterURL = "{}{}/{}".format(master_url, self.Config['master_url_endpoint'], master_lookup_id)

	def _create_provider(self, path: str):
		if path.startswith("zk://"):
			self.Provider = provider.ZooKeeperProvider(self.App, path)
		elif path.startswith("http://"):
			self.Provider = provider.HTTPProvider(self.App, path)
		else:
			self.Provider = provider.FileSystemProvider(self.App, path)

	# TODO: what service uses this?
	def time(self):
		return self.App.time()

	# TODO: where is this called from?
	def ensure_future_update(self, loop):
		return asyncio.ensure_future(self._do_update(), loop=loop)

	async def _do_update(self):
		updated = await self.load()
		if updated:
			self.PubSub.publish("bspump.Lookup.changed!")

	async def load(self) -> bool:
		data = self.Provider.load()
		if data is not None:
			try:
				await self.Cache.save(data)
			except Exception as e:
				L.warning("Error writing data to cache: {}".format(e))
		else:
			# Load from cache only the first time, when no data is loaded
			if self.IsLoaded:
				return False
			L.warning("No data loaded from {}. Loading from cache.".format(self.Provider.Id))
			data = await self.Cache.load()
			if data is None:
				L.warning("No data loaded from cache {}".format(self.Provider.Id))
				return False
		self.deserialize(data)
		return True

	def serialize(self):
		raise NotImplementedError("Lookup '{}' serialize() method not implemented".format(self.Id))

	def deserialize(self, data):
		raise NotImplementedError("Lookup '{}' deserialize() method not implemented".format(self.Id))

	# TODO: what service uses this?
	def rest_get(self):
		return {
			"Id": self.Id,
			"ETag": self.ETag,
			"MasterURL": self.MasterURL,
		}

	def is_master(self):
		return self.MasterURL is None


class MappingLookup(Lookup, collections.abc.Mapping):
	pass


class AsyncLookupMixin(Lookup):
	"""
	AsyncLookupMixin makes sure the value from the lookup is obtained asynchronously.
	AsyncLookupMixin is to be used for every technology that is external to BSPump,
	respective that require a connection to resource server such as SQL etc.
	"""

	async def get(self, key):
		raise NotImplementedError()


class DictionaryLookup(MappingLookup):

	def __init__(self, app, id=None, config=None, lazy=False):
		self.Dictionary = {}
		super().__init__(app, id, config=config, lazy=lazy)


	def __getitem__(self, key):
		return self.Dictionary.__getitem__(key)

	def __iter__(self):
		return self.Dictionary.__iter__()

	def __len__(self):
		return self.Dictionary.__len__()


	def serialize(self):
		return (json.dumps(self.Dictionary)).encode('utf-8')

	def deserialize(self, data):
		self.Dictionary.update(json.loads(data.decode('utf-8')))

	# REST

	def rest_get(self):
		rest = super().rest_get()
		rest["Dictionary"] = self.Dictionary
		return rest

	def set(self, dictionary: dict):
		if self.MasterURL is not None:
			L.warning("'master_url' provided, set() method can not be used")

		self.Dictionary.clear()
		self.Dictionary.update(dictionary)
