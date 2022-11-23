import asyncio
import collections.abc
import json
import logging
from typing import Optional

import asab

from .lookupprovider import LookupProviderABC

###

L = logging.getLogger(__name__)

###


class Lookup(asab.ConfigObject):
	"""
	Description:

	:return:
	"""

	ConfigDefaults = {
		"source_url": "",  # Specifies complete url to source file
		# zk://zookeeper1:2181/base/path/to/config.yaml
		# zk:///base/path/to/config.yaml  ==  zk:/base/path/to/config.yaml
		# zk:///./path/to/config.yaml  ==  zk:/./path/to/config.yaml
		# http://localhost:8080/path/to/config.yaml
		# file:/root/path/to/config.yaml  ==  /root/path/to/config.yaml

		# Backwards compatibility
		"master_url": "http://localhost:8080",
		"master_url_endpoint": "/bspump/v1/lookup/",
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
		self.Provider: Optional[LookupProviderABC] = None

		url = self.Config.get("source_url", "").strip()
		if len(url) == 0:
			# Construct URL from the old "master_" params
			server = self.Config.get("master_url", "").strip()
			if len(server) == 0:
				L.error("Neither `source_url` nor `master_url` specified in lookup {} config.".format(self.Id))
				return
			if not server.startswith("http:"):
				server = "http://{}".format(server)
			server = server.strip("/")
			master_url_endpoint = self.Config["master_url_endpoint"].strip("/")
			master_lookup_id = self.Config["master_lookup_id"]
			if master_lookup_id == "":
				master_lookup_id = self.Id
			url = "{}/{}/{}".format(server, master_url_endpoint, master_lookup_id)
		self._create_provider(url)

	def __getitem__(self, key):
		raise NotImplementedError("Lookup '{}' __getitem__() method not implemented".format(self.Id))

	def __iter__(self):
		raise NotImplementedError("Lookup '{}' __iter__() method not implemented".format(self.Id))

	def __len__(self):
		raise NotImplementedError("Lookup '{}' __len__() method not implemented".format(self.Id))

	def __contains__(self, item):
		raise NotImplementedError("Lookup '{}' __contains__() method not implemented".format(self.Id))

	def _create_provider(self, path: str):
		"""
		Description:

		:return:
		"""
		if path.startswith("zk:"):
			from bspump.zookeeper import ZooKeeperBatchLookupProvider
			self.Provider = ZooKeeperBatchLookupProvider(self, path)
			self.MasterURL = path
		elif path.startswith("http:") or path.startswith("https:"):
			from bspump.http import HTTPBatchLookupProvider
			config = {}
			if "use_cache" in self.Config:
				config["use_cache"] = self.Config.getboolean("use_cache")
			if "cache_dir" in self.Config:
				config["cache_dir"] = self.Config.get("source_url", None)
			self.Provider = HTTPBatchLookupProvider(self, path, config=config)
			self.MasterURL = path
		else:
			from bspump.file import FileBatchLookupProvider
			# Local file source -> lookup is considered master
			self.Provider = FileBatchLookupProvider(self, path)
			self.MasterURL = None

	def time(self):
		"""
		Description:

		:return:
		"""
		return self.App.time()

	def ensure_future_update(self, loop):
		"""
		Description:

		:return:
		"""
		return asyncio.ensure_future(self._do_update())

	async def _do_update(self):
		"""
		Description:

		:return:
		"""
		updated = await self.load()
		if updated:
			L.warning(f"{self.Id} bspump.Lookup.changed!")
			self.PubSub.publish("bspump.Lookup.changed!")

	async def load(self) -> bool:
		"""
		Description:

		:return:
		"""
		data = await self.Provider.load()
		if data is None or data is False:
			L.warning("No data loaded from {}.".format(self.Provider.Id))
			return False
		self.deserialize(data)
		return True

	def serialize(self):
		"""
		Description:

		:return:
		"""
		raise NotImplementedError("Lookup '{}' serialize() method not implemented".format(self.Id))

	def deserialize(self, data):
		"""
		Description:

		:return:
		"""
		raise NotImplementedError("Lookup '{}' deserialize() method not implemented".format(self.Id))

	def rest_get(self):
		"""
		Description:

		:return:
		"""
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
	"""
	Description:

	:return:
	"""
	pass


class AsyncLookupMixin(Lookup):
	"""
	Description:

	:return:
	"""

	async def get(self, key):
		raise NotImplementedError()


class DictionaryLookup(MappingLookup):
	"""
	Description:

	:return:
	"""

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
		"""
		Description:

		:return:
		"""
		return (json.dumps(self.Dictionary)).encode('utf-8')

	def deserialize(self, data):
		"""
		Description:

		:return:
		"""
		try:
			self.Dictionary.update(json.loads(data.decode('utf-8')))
		except Exception as e:
			L.error("Lookup {} failed to deserialize loaded data: {}".format(self.Id, e))

	# REST

	def rest_get(self):
		"""
		Description:

		:return:
		"""
		rest = super().rest_get()
		rest["Dictionary"] = self.Dictionary
		return rest

	def set(self, dictionary: dict):
		"""
		Description:

		:return:
		"""
		if self.is_master() is False:
			L.warning("'master_url' provided, set() method can not be used")

		self.Dictionary.clear()
		self.Dictionary.update(dictionary)
