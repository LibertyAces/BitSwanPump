import abc
import asyncio
import logging
import os
import urllib.parse

import aiohttp
import aiozk

import asab


###

L = logging.getLogger(__name__)

###


class ProviderABC(abc.ABC, asab.ConfigObject):
	def __init__(self, app, id=None, config=None):
		super().__init__()
		self.Id = "provider:{}".format(id if id is not None else self.__class__.__name__)
		self.App = app

	async def load(self):
		raise NotImplementedError()

	async def save(self, data):
		raise NotImplementedError()


class ZooKeeperProvider(ProviderABC):
	def __init__(self, app, url, id=None, config=None):
		super().__init__(app, id, config)
		url_parts = urllib.parse.urlparse(url)
		self.Servers = url_parts.netloc
		self.Path = url_parts.path
		self.ZKClient = aiozk.ZKClient(self.Servers)

	async def load(self):
		established = self._open_connection()
		if not established:
			L.error("Cannot load data from zookeeper")
			return
		try:
			data = await self.ZKClient.get_data(self.Path)
		except Exception as e:
			L.error("Failed to fetch '{}': {}".format(self.Path, e))
			data = None
		finally:
			await self._close_connection()
		return data

	async def save(self, data):
		raise NotImplementedError()

	async def _open_connection(self):
		self.ZKClient = aiozk.ZKClient(self.Servers)
		await self.ZKClient.start()

	async def _close_connection(self):
		if self.ZKClient is None:
			return
		await self.ZKClient.close()
		self.ZKClient = None


class HTTPProvider(ProviderABC):
	ConfigDefaults = {
		"master_timeout": 30
	}

	def __init__(self, app, path, id=None, config=None):
		super().__init__(app, id, config)
		self.URL = path
		self.Timeout = self.Config.get("master_timeout")
		if self.Timeout is not None:
			self.Timeout = float(self.Timeout)

	async def load(self):
		async with aiohttp.ClientSession() as session:
			try:
				response = await session.get(self.URL, timeout=self.Timeout)
			except asyncio.TimeoutError as e:
				L.warning("Connection to '{}' timed out: {}".format(self.URL, e))
				return None
			except Exception as e:
				L.error("Failed to connect to '{}': {}".format(self.URL, e))
				return None
			if response.status != 200:
				L.warning("{} responded with {}: {}".format(self.URL, response.status, response.reason))
				return None
			data = await response.read()
		return data

	async def save(self, data):
		raise NotImplementedError()


class FileSystemProvider(ProviderABC):
	def __init__(self, app, path, id=None, config=None):
		super().__init__(app, id, config)
		self.Path = path

	async def load(self):
		if not os.path.isfile(self.Path):
			return None
		if not os.access(self.Path, os.R_OK):
			return None
		try:
			with open(self.Path, 'rb') as f:
				data = f.read()
			return data
		except Exception as e:
			L.warning("Failed to read content of lookup cache '{}' from '{}': {}".format(self.Id, self.Path, e))
			os.unlink(self.Path)
		return None

	async def save(self, data):
		dirname = os.path.dirname(self.Path)
		if not os.path.isdir(dirname):
			os.makedirs(dirname)
		with open(self.Path, 'wb') as fo:
			fo.write(data)
