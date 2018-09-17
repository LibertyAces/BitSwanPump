from ..abc.processor import Processor
from ..abc.generator import Generator

#

class DictKeys2ListProcessor(Processor):
	def process(self, context, event:dict) -> list:
		return [*event.keys()]

#

class DictValues2ListProcessor(Processor):
	def process(self, context, event:dict) -> list:
		return [*event.values()]

#

class DictItems2ListProcessor(Processor):
	def process(self, context, event:dict) -> list:
		return [*event.items()]

#

class DictKeysGenerator(Generator):
	
	def process(self, context, event:dict):
		
		def generate():
			for item in event.keys():
				yield item

		return generate()

#

class DictValuesGenerator(Generator):
	
	def process(self, context, event:dict):
		
		def generate():
			for item in event.values():
				yield item

		return generate()

#

class DictItemsGenerator(Generator):
	
	def process(self, context, event:dict):
		
		def generate():
			for item in event.items():
				yield item

		return generate()
