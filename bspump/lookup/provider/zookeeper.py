import logging
import urllib.parse
import aiozk
import asab.zookeeper

from .abc import LookupProviderABC

###

L = logging.getLogger(__name__)

###


def _build_client(url):
	parsed = urllib.parse.urlparse(url)
	zk_client = aiozk.ZKClient(parsed.netloc)
	path = parsed.path
	return zk_client, path


class ZooKeeperLookupProvider(LookupProviderABC):
	def __init__(self, app, lookup, url, id=None, config=None):
		super().__init__(app, lookup, id, config)
		self.ZKClient = None
		self.Path = None
		# TODO: use the dedicated function once it's ready
		# self.ZKClient, self.Path = asab.zookeeper.build_client(url)
		self.ZKClient, self.Path = _build_client(url)

	async def load(self):
		try:
			await self.ZKClient.start()
		except Exception as e:
			L.error("Cannot start zookeeper client: {}".format(e))
			return
		try:
			data = await self.ZKClient.get_data()
		except Exception as e:
			L.error("Failed to fetch '{}': {}".format(self.Path, e))
			data = None
		finally:
			await self.ZKClient.close()
		return data
