import json
from .. import Processor

class JSON2DictProcessor(Processor):

	def process(self, event):
		return json.loads(event)
