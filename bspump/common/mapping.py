import collections.abc

from ..abc.processor import Processor
from ..abc.generator import Generator

#

class MappingKeysProcessor(Processor):
	def process(self, context, event:collections.abc.Mapping) -> list:
		return [*event.keys()]

#

class MappingValuesProcessor(Processor):
	def process(self, context, event:collections.abc.Mapping) -> list:
		return [*event.values()]

#

class MappingItemsProcessor(Processor):
	def process(self, context, event:collections.abc.Mapping) -> list:
		return [*event.items()]

#

class MappingKeysGenerator(Generator):
	
	def process(self, context, event:collections.abc.Mapping):
		
		def generate():
			for item in event.keys():
				yield item

		return generate()

#

class MappingValuesGenerator(Generator):
	
	def process(self, context, event:collections.abc.Mapping):
		
		def generate():
			for item in event.values():
				yield item

		return generate()

#

class MappingItemsGenerator(Generator):
	
	def process(self, context, event:collections.abc.Mapping):
		
		def generate():
			for item in event.items():
				yield item

		return generate()
