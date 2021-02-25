import asyncio
import collections.abc
import json
import logging
from typing import Optional

import asab

from bspump.abc import lookupprovider

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
		"source_url": "",  # Specifies complete url to source file
		# zk://zookeeper1:2181/base/path/to/config.yaml
		# zk:///base/path/to/config.yaml  ==  zk:/base/path/to/config.yaml
		# zk:///./path/to/config.yaml  ==  zk:/./path/to/config.yaml
		# http://localhost:8080/path/to/config.yaml
		# file:/root/path/to/config.yaml  ==  /root/path/to/config.yaml

		# Backwards compatibility
		"master_url": "",
		"master_url_endpoint": "",
		"master_lookup_id": "",  # If not empty, it specify the lookup id that will be used for loading from master
	}

	def __init__(self, app, id=None, config=None, lazy=False):
		_id = id if id is not None else self.__class__.__name__
		super().__init__("lookup:{}".format(_id), config=config)
		self.Id = _id
		self.App = app
		self.Loop = app.Loop
		self.Lazy = lazy

		self.PubSub = asab.PubSub(app)

		self.MasterURL = None
		self.Provider: Optional[lookupprovider.LookupProviderABC] = None

		url = self.Config.get("source_url", "").strip()
		if len(url) > 0:
			self._create_provider(url)
		else:
			url = self.Config.get("master_url", "")
			if len(url) > 0:
				url = url.rstrip("/")
				master_lookup_id = self.Config["master_lookup_id"]
				if master_lookup_id == "":
					master_lookup_id = self.Id
				self.MasterURL = "{}{}/{}".format(url, self.Config["master_url_endpoint"], master_lookup_id)
				self.Provider = lookupprovider.HTTPBatchProvider(self, self.MasterURL)

	def __getitem__(self, key):
		raise NotImplementedError("Lookup '{}' __getitem__() method not implemented".format(self.Id))

	def __iter__(self):
		raise NotImplementedError("Lookup '{}' __iter__() method not implemented".format(self.Id))

	def __len__(self):
		raise NotImplementedError("Lookup '{}' __len__() method not implemented".format(self.Id))

	def __contains__(self, item):
		raise NotImplementedError("Lookup '{}' __contains__() method not implemented".format(self.Id))

	def _create_provider(self, path: str):
		if path.startswith("zk:"):
			self.Provider = lookupprovider.ZooKeeperBatchProvider(self, path)
			self.MasterURL = path
		elif path.startswith("http:") or path.startswith("https:"):
			self.Provider = lookupprovider.HTTPBatchProvider(self, path)
			self.MasterURL = path
		else:
			# Local file source -> lookup is considered master
			self.Provider = lookupprovider.FileBatchProvider(self, path)
			self.MasterURL = None

	def time(self):
		return self.App.time()

	def ensure_future_update(self, loop):
		return asyncio.ensure_future(self._do_update(), loop=loop)

	async def _do_update(self):
		updated = await self.load()
		if updated:
			self.PubSub.publish("bspump.Lookup.changed!")

	async def load(self) -> bool:
		data = await self.Provider.load()
		if data is None:
			L.warning("No data loaded from {}.".format(self.Provider.Id))
			return False
		self.deserialize(data)
		return True

	def serialize(self):
		# TODO: probably not necessary since Lookup is read only
		raise NotImplementedError("Lookup '{}' serialize() method not implemented".format(self.Id))

	def deserialize(self, data):
		raise NotImplementedError("Lookup '{}' deserialize() method not implemented".format(self.Id))

	def rest_get(self):
		response = {
			"Id": self.Id
		}
		if self.Provider.ETag is not None:
			response["ETag"] = self.Provider.ETag
		if self.MasterURL is not None:
			response["MasterURL"] = self.MasterURL
		return response

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

	def get(self, key):
		if key in self.Dictionary:
			return self.__getitem__(key)
		return None

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
