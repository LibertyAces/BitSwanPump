import logging
import asab.zookeeper

from .abc import LookupProviderABC

###

L = logging.getLogger(__name__)

###


class ZooKeeperLookupProvider(LookupProviderABC):
	ConfigDefaults = {
		"url": ""
	}

	def __init__(self, app, url, id=None, config=None):
		super().__init__(app, id, config)
		zookeeper_section = self.Config.get("url")
		self.Client = asab.zookeeper.build_client(app.Config, )
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