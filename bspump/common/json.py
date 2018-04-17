import json
from ..abc.processor import Processor

class JSONParserProcessor(Processor):

	def process(self, context, event):
		return json.loads(event)
