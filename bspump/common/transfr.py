import collections.abc

from ..abc.processor import Processor


class MappingTransformator(Processor):
	"""
	Description:

	"""


	def __init__(self, app, pipeline, id=None, config=None):
		"""
		Description:

		"""
		super().__init__(app, pipeline, id=id, config=config)
		self.Mapping = self.build(app)
		self.Default = None


	def build(self, app):
		"""
		Description:

		"""
		raise NotImplementedError()


	def _map(self, item):
		"""
		Description:

		:return: ??

		|

		"""
		key, value = item
		t = self.Mapping.get(key)
		if t is not None:
			return t(key, value)
		elif self.Default is not None:
			return self.Default(key, value)
		else:
			return key, value


	def process(self, context, event: collections.abc.Mapping) -> dict:
		"""
		Description:

		:return: dict(map(self._map, event.items()))

		|

		"""
		return dict(map(self._map, event.items()))
