import logging
import os
import struct

import aiohttp
import asyncio

import asab

from .abc import LookupBatchProviderABC

###

L = logging.getLogger(__name__)

###


class HTTPBatchProvider(LookupBatchProviderABC):
	"""
	Fetches lookup data from given URL over HTTP. This provider embeds loading and caching functions of the
	original bspump.Lookup in "slave" mode.
	"""

	ConfigDefaults = {
		"master_timeout": 30,
		"use_cache": "yes",
		"cache_dir": ""
	}

	def __init__(self, lookup, url, id=None, config=None):
		super().__init__(lookup, url, id, config)
		self.Timeout = self.Config.get("master_timeout")
		if self.Timeout is not None:
			self.Timeout = float(self.Timeout)
		self.CachePath = None
		if self.Config.getboolean("use_cache"):
			cache_path = self.Config.get("cache_dir", "").strip()
			if len(cache_path) == 0:
				cache_path = os.path.abspath(asab.Config.get("general", "var_dir", ""))
			if len(cache_path) == 0:
				L.warning("No cache path specified. Cache disabled.")
			self.CachePath = os.path.join(cache_path, "lookup_{}.cache".format(self.Id))

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
				L.warning("Failed to contact lookup master at '{}': {}".format(self.URL, e))
				return self.load_from_cache()
			except asyncio.TimeoutError as e:
				L.warning("Failed to contact lookup master at '{}' (timeout): {}".format(self.URL, e))
				return self.load_from_cache()

			if response.status == 304:
				L.info("Lookup '{}' is up to date.".format(self.Id))
				return False

			if response.status == 404:
				L.warning("Lookup '{}' was not found at the provider.".format(self.Id))
				return self.load_from_cache()

			if response.status == 501:
				L.warning("Lookup '{}' method does not support serialization.".format(self.Id))
				return False

			if response.status != 200:
				L.warning("Failed to get '{}' lookup from '{}' master.".format(self.Id, self.URL))
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
		# Load the ETag from cached file, if have one
		if not os.path.isfile(self.CachePath):
			return False

		if not os.access(self.CachePath, os.R_OK):
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
		dirname = os.path.dirname(self.CachePath)
		if not os.path.isdir(dirname):
			os.makedirs(dirname)

		with open(self.CachePath, 'wb') as fo:
			# Write E-Tag and '\n'
			etag_b = self.ETag.encode('utf-8')
			fo.write(struct.pack(r"<L", len(etag_b)) + etag_b + b'\n')

			# Write Data
			fo.write(data)
