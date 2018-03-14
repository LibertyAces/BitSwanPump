import json
from .. import Processor

class JSONParserProcessor(Processor):

	def process(self, event):
		return json.loads(event)
