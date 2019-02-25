import json
from ..abc.processor import Processor


class DictToJsonParser(Processor):

	def process(self, context, event):
		assert isinstance(event, dict)
		return json.dumps(event)


class JsonToDictParser(Processor):

	def process(self, context, event):
		assert isinstance(event, str)
		return json.loads(event)
