import json
from ..abc.processor import Processor


class DictToJsonParser(Processor):

	def process(self, context, event):
		return json.dumps(event)


class JsonToDictParser(Processor):

	def process(self, context, event):
		return json.loads(event)
