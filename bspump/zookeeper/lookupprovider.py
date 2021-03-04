import logging
import asab

from asab.zookeeper import build_client
from bspump.abc.lookupprovider import LookupBatchProviderABC

###

L = logging.getLogger(__name__)

###


class ZooKeeperBatchLookupProvider(LookupBatchProviderABC):
	"""
	Fetches lookup data from given zookeeper URL.
	"""

	def __init__(self, lookup, url, id=None, config=None):
		super().__init__(lookup, url, id, config)
		self.ZKClient, self.Path = build_client(asab.Config, self.URL)

	async def load(self):
		try:
			await self.ZKClient.start()
		except Exception as e:
			L.error("Cannot start zookeeper client: {}".format(e))
			return None
		try:
			data = await self.ZKClient.get_data(self.Path)
		except Exception as e:
			L.error("Failed to fetch '{}': {}".format(self.Path, e))
			data = None
		finally:
			await self.ZKClient.close()
		return data
