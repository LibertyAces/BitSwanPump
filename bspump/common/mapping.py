import collections.abc

from ..abc.processor import Processor
from ..abc.generator import Generator


class MappingKeysProcessor(Processor):
	"""
	Mapping Keys Processor
	"""
	def process(self, context, event: collections.abc.Mapping) -> list:
		"""
		process is a method of a Mapping Keys Processor
		"""
		return [*event.keys()]


class MappingValuesProcessor(Processor):
	def process(self, context, event: collections.abc.Mapping) -> list:
		return [*event.values()]


class MappingItemsProcessor(Processor):
	def process(self, context, event: collections.abc.Mapping) -> list:
		return [*event.items()]


class MappingKeysGenerator(Generator):

	async def generate(self, context, event, depth):
		for item in event.keys():
			self.Pipeline.inject(context, item, depth)


class MappingValuesGenerator(Generator):

	async def generate(self, context, event, depth):
		for item in event.values():
			self.Pipeline.inject(context, item, depth)


class MappingItemsGenerator(Generator):

	async def generate(self, context, event, depth):
		for item in event.items():
			self.Pipeline.inject(context, item, depth)
