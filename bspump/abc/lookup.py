import abc
import json
from .config import ConfigObject


class Lookup(abc.ABC, ConfigObject):

	def __init__(self, app, lookup_id):
		super().__init__("lookup:{}".format(lookup_id), config=None)
		self.lookup={}
		self.load()

	def __getitem__(self, key):
		return self.lookup[key]

	def __setitem__(self, key, val):
		self.lookup[key] = val

	@abc.abstractmethod
	def load(self):
		pass

	def get(self, key, default=None):
		return self.lookup.get(key, default)


	def load_json_file(self, fname):

		if fname.endswith(".gz"):
			import gzip
			f = gzip.open(fname, 'rb')

		elif fname.endswith(".bz2"):
			import bz2
			f = bz2.open(fname, 'rb')

		elif fname.endswith(".xz") or fname.endswith(".lzma"):
			import lzma
			f = lzma.open(fname, 'rb')

		else:
			f = open(fname, 'rb')

		jdata = json.loads(f.read().decode('utf-8'))
		f.close()
		return jdata
