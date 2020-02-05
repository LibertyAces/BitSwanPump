import abc
import asyncio
import collections.abc
import json
import logging
import os
import struct

import aiohttp

import asab

###

L = logging.getLogger(__name__)

###


class Lookup(abc.ABC, asab.ConfigObject):
	"""
	Lookups serve for fast data searching in lists of key-value type. They can subsequently be localized and used in pipeline objects (processors and the like). Each lookup requires a statically or dynamically created value list.

	If the "lazy" parameter in the constructor is set to True, no load method is called and the user is expected to call it when necessary.
	"""


	ConfigDefaults = {
		"master_url": "",  # If not empty, a lookup is in slave mode (will load data from master or cache)
		"master_lookup_id": "",  # If not empty, it specify the lookup id that will be used for loading from master
		"master_timeout": 30,  # In secs.
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
		master_url = self.Config['master_url']
		if master_url:
			while master_url[-1] == '/':
				master_url = master_url[:-1]
			master_lookup_id = self.Config['master_lookup_id']
			if master_lookup_id == "":
				master_lookup_id = self.Id
			self.MasterURL = master_url + '/bspump/v1/lookup/' + master_lookup_id
		else:
			self.MasterURL = None  # No master is defined


	def time(self):
		return self.App.time()


	def ensure_future_update(self, loop):
		return asyncio.ensure_future(self._do_update(), loop=loop)


	async def _do_update(self):
		if self.is_master():
			updated = await self.load()
		else:
			updated = await self.load_from_master()

		if updated:
			self.PubSub.publish("bspump.Lookup.changed!")


	@abc.abstractmethod
	async def load(self) -> bool:
		"""
		Return True is lookup has been changed.

		Example:

.. code:: python

		async def load(self):
			self.set(bspump.load_json_file('./examples/data/country_names.json'))
			return True
		"""
		pass

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
				L.info("The '{}' lookup is actual.".format(self.Id))
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


class MappingLookup(Lookup, collections.abc.Mapping):
	pass


class AsyncLookupMixin(Lookup):
	"""
	AsyncLookupMixin makes sure the value from the lookup is obtained asynchronously.
	AsyncLookupMixin is to be used for every technology that is external to BSPump,
	respective that require a connection to resource server such as SQL etc.
	"""

	@abc.abstractmethod
	async def get(self, key):
		pass


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
