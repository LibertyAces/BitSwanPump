import json
from .. import Processor

class JSON2DictProcessor(Processor):

	def process(self, data):
		return json.loads(data)
