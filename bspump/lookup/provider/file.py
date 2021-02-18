import logging
import os

from .abc import LookupProviderABC

###

L = logging.getLogger(__name__)

###


class FileSystemLookupProvider(LookupProviderABC):
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
