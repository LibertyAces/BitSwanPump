import logging
import os
import struct

import aiohttp
import asyncio

import asab

from bspump.abc.lookupprovider import LookupBatchProviderABC

###

L = logging.getLogger(__name__)

###


class HTTPBatchLookupProvider(LookupBatchProviderABC):
	"""
	Fetches lookup data from given URL over HTTP. This lookupprovider embeds loading and caching functions of the
	original bspump.Lookup in "slave" mode.
	"""

	ConfigDefaults = {
		"master_timeout": 30,
		"use_cache": "yes",
		"cache_dir": ""
	}

	def __init__(self, lookup, url, id=None, config=None):
		super().__init__(lookup, url, id, config=config)
		self.Timeout = self.Config.get("master_timeout")
		self.UseCache = self.Config.getboolean("use_cache")
		if self.Timeout is not None:
			self.Timeout = float(self.Timeout)
		self.CachePath = None
		if self.UseCache is True:
			cache_path = self.Config.get("cache_dir", "").strip()
			if len(cache_path) == 0 and "general" in asab.Config and "var_dir" in asab.Config["general"]:
				cache_path = os.path.abspath(asab.Config["general"]["var_dir"])
				self.CachePath = os.path.join(cache_path, "lookup_{}.cache".format(self.Id))
			else:
				self.UseCache = False
				L.warning("No cache path specified. Cache disabled.")

	async def load(self):
		headers = {}
		if self.ETag is not None:
			headers['ETag'] = self.ETag

		async with aiohttp.ClientSession() as session:
			try:
				response = await session.get(
					self.URL,
					headers=headers,
					timeout=float(self.Config['master_timeout'])
				)
			except aiohttp.ClientConnectorError as e:
				L.warning("{}: Failed to contact lookup master at '{}': {}".format(self.Id, self.URL, e))
				return self.load_from_cache()
			except asyncio.TimeoutError as e:
				L.warning("{}: Failed to contact lookup master at '{}' (timeout): {}".format(self.Id, self.URL, e))
				return self.load_from_cache()

			if response.status == 304:
				L.info("Lookup '{}' is up to date with the provider {}.".format(self.Id, self.URL))
				return False

			if response.status == 404:
				L.warning("{}: lookup was not found at the lookup provider {}".format(self.Id, self.URL))
				return self.load_from_cache()

			if response.status == 501:
				L.warning("{}: master '{}' does not support serialization.".format(self.Id, self.URL))
				return False

			if response.status != 200:
				L.warning("{}: Failed to get lookup from master {}".format(self.Id, self.URL))
				return self.load_from_cache()
			data = await response.read()
			self.ETag = response.headers.get('ETag')
			if self.CachePath is not None:
				self.save_to_cache(data)
		return data

	def load_from_cache(self):
		"""
		Load the lookup data (bytes) from cache.
		"""
		if self.UseCache is False:
			return False
		# Load the ETag from cached file, if have one
		if not os.path.isfile(self.CachePath):
			L.warning("Cache '{}': not a file".format(self.CachePath))
			return False

		if not os.access(self.CachePath, os.R_OK):
			L.warning("Cannot read cache from '{}'".format(self.CachePath))
			return False

		try:
			with open(self.CachePath, 'rb') as f:
				tlen, = struct.unpack(r"<L", f.read(struct.calcsize(r"<L")))
				etag_b = f.read(tlen)
				self.ETag = etag_b.decode('utf-8')
				f.read(1)
				data = f.read()
			return data
		except Exception as e:
			L.warning("Failed to read content of lookup cache '{}' from '{}': {}".format(self.Id, self.CachePath, e))
			os.unlink(self.CachePath)
		return False

	def save_to_cache(self, data):
		if self.UseCache is False:
			return
		dirname = os.path.dirname(self.CachePath)
		if not os.path.isdir(dirname):
			os.makedirs(dirname)

		with open(self.CachePath, 'wb') as fo:
			# Write E-Tag and '\n'
			etag_b = self.ETag.encode('utf-8')
			fo.write(struct.pack(r"<L", len(etag_b)) + etag_b + b'\n')

			# Write Data
			fo.write(data)
