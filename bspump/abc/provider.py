

class ProviderABC(abc.ABC):

	async def load(self):
		raise NotImplementedError("Provider '{}' load() method not implemented".format(self.Id))


class HTTPProvider(ProviderABC):
	def __init__(self):
		pass


class ZooKeeperProvider(ProviderABC):
	def __init__(self):
		pass
