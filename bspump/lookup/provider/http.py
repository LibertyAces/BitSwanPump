import logging
import aiohttp
import asyncio

from .abc import LookupProviderABC

###

L = logging.getLogger(__name__)

###


class HTTPLookupProvider(LookupProviderABC):
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
