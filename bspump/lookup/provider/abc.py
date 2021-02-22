import abc
import asab


class LookupProviderABC(abc.ABC, asab.ConfigObject):
	def __init__(self, app, lookup, id=None, config=None):
		super().__init__()
		self.Id = "provider:{}".format(id if id is not None else self.__class__.__name__)
		self.Lookup = lookup
		self.App = app

	async def load(self):
		raise NotImplementedError()
