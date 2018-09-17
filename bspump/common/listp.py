from ..abc.generator import Generator

class ListGenerator(Generator):
	
	def process(self, context, event:list):
		
		def generate():
			for item in event:
				yield item

		return generate()
