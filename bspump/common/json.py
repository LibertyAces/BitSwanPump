import json
from ..abc.processor import Processor

class JSONParser(Processor):

	def process(self, context, event):
		return json.loads(event)
