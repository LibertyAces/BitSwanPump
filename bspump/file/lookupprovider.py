import logging
import os

import asab.proactor

from bspump.abc.lookupprovider import LookupBatchProviderABC

###

L = logging.getLogger(__name__)

###


class FileBatchLookupProvider(LookupBatchProviderABC):
	"""
	Loads lookup data from a file on local filesystem.
	"""

	def __init__(self, lookup, url, id=None, config=None):
		super().__init__(lookup, url, id, config)
		self.App.add_module(asab.proactor.Module)
		self.ProactorService = self.App.get_service("asab.ProactorService")

	async def load(self):
		result = await self.ProactorService.execute(
			self.load_on_thread,
		)
		return result

	def load_on_thread(self):
		if not os.path.isfile(self.URL):
			L.warning("Source '{}' is not a file".format(self.URL))
			return None
		if not os.access(self.URL, os.R_OK):
			L.warning("Insufficient permissions: '{}'".format(self.URL))
			return None
		try:
			with open(self.URL, 'rb') as f:
				data = f.read()
			return data
		except Exception as e:
			L.warning("Failed to read content of file '{}': {}".format(self.URL, e))
		return None

	async def save(self, data):
		dirname = os.path.dirname(self.URL)
		if not os.path.isdir(dirname):
			os.makedirs(dirname)
		with open(self.URL, 'wb') as fo:
			fo.write(data)
