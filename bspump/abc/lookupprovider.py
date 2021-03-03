import abc

import asab


class LookupProviderABC(abc.ABC, asab.ConfigObject):
	def __init__(self, lookup, url, id=None, config=None):
		self.Id = "lookupprovider:{}".format(id if id is not None else self.__class__.__name__)
		super().__init__(config_section_name=self.Id, config=config)
		self.Lookup = lookup
		self.App = lookup.App
		self.URL = url
		self.ETag = None

	async def load(self):
		raise NotImplementedError()


class LookupBatchProviderABC(LookupProviderABC):
	pass
