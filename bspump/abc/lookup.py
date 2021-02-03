import asyncio
import collections.abc
import json
import logging
import os
import struct

import aiohttp

import asab
import asab.zookeeper

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
		"zookeeper_section": "",  # Points to where zookeeper connection is defined,
		"zookeeper_path": "",
		"supported_extensions": "pkl pkl.gz"
	}


	def __init__(self, app, id=None, config=None, lazy=False):
		_id = id if id is not None else self.__class__.__name__
		super().__init__("lookup:{}".format(_id), config=config)

		self.App = app
		self.Loop = app.Loop
		self.Lazy = lazy

		self.Id = _id
		self.PubSub = asab.PubSub(app)

		self.ETag = None

		self.ProvidersPath = self.Config.get("providers", "").strip()
		if len(self.ProvidersPath) == 0:
			self.ProvidersPath = self.Config.get("master_url", "").strip()  # backwards compatibility
		self._parse_providers()

		# TODO: only one provider should be expected
		# TODO: move connection handling to providers
		# TODO: move load methods to providers

		master_url = self.Config['master_url']
		if master_url:
			while master_url[-1] == '/':
				master_url = master_url[:-1]
			master_lookup_id = self.Config['master_lookup_id']
			if master_lookup_id == "":
				master_lookup_id = self.Id
			self.MasterURL = "{}{}/{}".format(master_url, self.Config['master_url_endpoint'], master_lookup_id)
		else:
			self.MasterURL = None  # No master is defined

		self.SupportedExtensions = None
		extensions = self.Config.get("supported_extensions", "").strip()
		if len(extensions) > 0:
			self.SupportedExtensions = re.split("\s+", extensions)

		self.ZooKeeperContainer = None
		zookeeper_section = self.Config.get("zookeeper_section", None)
		zookeeper_path = self.Config.get("zookeeper_path", None)
		if zookeeper_section is not None and zookeeper_path is not None:
			zookeeper_svc = app.get_service("asab.ZooKeeperService")
			config = {
				"path": zookeeper_path.replace("zk://", "")
			}
			self.ZooKeeperContainer = asab.zookeeper.ZooKeeperContainer(
				app,
				zookeeper_section,
				config=config
			)
			zookeeper_svc.register_container(self.ZooKeeperContainer)

	def _parse_providers(self):
		self.Providers = []
		if len(self.ProvidersPath) == 0:
			L.error("No provider specified.")
			return
		providers = re.split("\s+", self.ProvidersPath)
		for provider in providers:
			self.create_provider(provider)

	def create_provider(self, path: str):
		if path.startswith("zk:"):
			self.Providers.append(provider.ZooKeeperProvider(path, self.App))
		elif path.startswith("http:") or path.startswith("https:"):
			self.Providers.append(provider.HTTPProvider(path, self.App))
		else:
			L.warning("No explicit provider stated in path '{}'. Assuming HTTP.".format(path))
			self.Providers.append(provider.HTTPProvider(path, self.App))

	def time(self):
		return self.App.time()


	def ensure_future_update(self, loop):
		return asyncio.ensure_future(self._do_update(), loop=loop)


	async def _do_update(self):
		if self.is_master():
			updated = await self.load()
		elif self.ZooKeeperContainer is not None:
			updated = await self.load_from_zookeeper()
		else:
			updated = await self.load_from_master()

		if updated:
			self.PubSub.publish("bspump.Lookup.changed!")


	async def load(self) -> bool:
		"""
		Return True is lookup has been changed.

		Example:

.. code:: python

		async def load(self):
			self.set(bspump.load_json_file('./examples/data/country_names.json'))
			return True
		"""
		raise NotImplementedError("Lookup '{}' serialize() method not implemented".format(self.Id))


	# Serialization

	def serialize(self):
		raise NotImplementedError("Lookup '{}' serialize() method not implemented".format(self.Id))

	def deserialize(self, data):
		raise NotImplementedError("Lookup '{}' deserialize() method not implemented".format(self.Id))

	# REST

	def rest_get(self):
		return {
			"Id": self.Id,
			"ETag": self.ETag,
			"MasterURL": self.MasterURL,
		}

	# Cache control

	def load_from_cache(self):
		"""
		Load the lookup data from a cache.
		Data (bytes) are read from a file and passed to deserialize function.
		"""
		path = os.path.join(os.path.abspath(asab.Config["general"]["var_dir"]), "lookup_{}.cache".format(self.Id))

		# Load the ETag from cached file, if have one
		if not os.path.isfile(path):
			return False

		if not os.access(path, os.R_OK):
			return False

		try:
			with open(path, 'rb') as f:
				tlen, = struct.unpack(r"<L", f.read(struct.calcsize(r"<L")))
				etag_b = f.read(tlen)
				self.ETag = etag_b.decode('utf-8')
				f.read(1)
				data = f.read()

			self.deserialize(data)

		except Exception as e:
			L.warning("Failed to read content of lookup cache '{}' from '{}': {}".format(self.Id, path, e))
			os.unlink(path)
			return False


		return True


	def save_to_cache(self, data):
		path = os.path.join(os.path.abspath(asab.Config["general"]["var_dir"]), "lookup_{}.cache".format(self.Id))
		dirname = os.path.dirname(path)
		if not os.path.isdir(dirname):
			os.makedirs(dirname)

		with open(path, 'wb') as fo:

			# Write E-Tag and '\n'
			etag_b = self.ETag.encode('utf-8')
			fo.write(struct.pack(r"<L", len(etag_b)) + etag_b + b'\n')

			# Write Data
			fo.write(data)

	# Master/slave mechanism

	def is_master(self):
		return self.MasterURL is None


	async def load_from_master(self):
		if self.MasterURL is None:
			L.error("'master_url' must be provided")
			return False

		headers = {}
		if self.ETag is not None:
			headers['ETag'] = self.ETag

		async with aiohttp.ClientSession() as session:

			try:
				response = await session.get(self.MasterURL, headers=headers, timeout=float(self.Config['master_timeout']))
			except aiohttp.ClientConnectorError as e:
				L.warning("Failed to contact lookup master at '{}': {}".format(self.MasterURL, e))
				return self.load_from_cache()
			except asyncio.TimeoutError as e:
				L.warning("Failed to contact lookup master at '{}' (timeout): {}".format(self.MasterURL, e))
				return self.load_from_cache()

			if response.status == 304:
				L.info("The '{}' lookup is up to date.".format(self.Id))
				return False

			if response.status == 404:
				L.warning("Lookup '{}'' was not found at the provider.".format(self.Id))
				return self.load_from_cache()

			if response.status == 501:
				L.warning("Lookup '{}' method does not support serialization.".format(self.Id))
				return False

			if response.status != 200:
				L.warning("Failed to get '{}' lookup from '{}' master.".format(self.Id, self.MasterURL))
				return self.load_from_cache()

			data = await response.read()
			self.ETag = response.headers.get('ETag')

		self.deserialize(data)

		L.info("The '{}' lookup was successfully loaded from master.".format(self.Id))

		self.save_to_cache(data)

		return True

	async def load_from_zookeeper(self) -> bool:
		# Find the actual file name
		if self.SupportedExtensions is None:
			L.warning("No supported file extensions specified.")
			return False

		file_list = await self.ZooKeeperContainer.get_children()
		for extension in self.SupportedExtensions:
			file_name = "{}.{}".format(self.ZoneName, extension)
			if file_name in file_list:
				break
		else:
			L.warning("Zone file '{}' not found".format(self.ZoneName))
			return False

		# Load the file
		L.info("Loading '{}'".format(file_name))
		try:
			raw_data = await self.ZooKeeperContainer.get_raw_data(file_name)
		except Exception as e:
			L.error("Failed to fetch '{}': {}".format(file_name, e))
			return False

		try:
			self.deserialize(raw_data)
		except Exception as e:
			L.error("Failed to deserialize '{}': {}".format(file_name, e))
			return False

		L.log(asab.LOG_NOTICE, "File '{}' successfully loaded".format(file_name))

		self.save_to_cache(raw_data)

		return True


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
