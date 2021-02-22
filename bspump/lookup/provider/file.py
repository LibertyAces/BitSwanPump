import logging
import os

from .abc import LookupBatchProviderABC

###

L = logging.getLogger(__name__)

###


class FileBatchProvider(LookupBatchProviderABC):
	def __init__(self, lookup, url, id=None, config=None):
		super().__init__(lookup, url, id, config)

	async def load(self):
		if not os.path.isfile(self.URL):
			return None
		if not os.access(self.URL, os.R_OK):
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
