import json
import simdjson
from ..abc.processor import Processor


class DictToJsonParser(Processor):

	def process(self, context, event):
		return simdjson.dumps(event)


class JsonToDictParser(Processor):

	def process(self, context, event):
		return simdjson.loads(event)


class SimdJsonParser(Processor):
	'''
	Fast JSON parser.
	Based on https://github.com/TkTech/pysimdjson
	'''

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		self._parser = simdjson.Parser()

	def process(self, context, event: bytes):
		return self._parser.parse(event)


class StdDictToJsonParser(Processor):

	def process(self, context, event):
		return json.dumps(event)


class StdJsonToDictParser(Processor):

	def process(self, context, event):
		return json.loads(event)


class DictToJsonBytesParser(Processor):
	"""
	DictToJsonBytesParser transforms a dictionary to JSON-string encoded in bytes.
	The encoding charset can be specified in the configuration in `encoding` field.
	"""
	ConfigDefaults = {
		'encoding': 'utf-8',
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		self.Encoding = self.Config['encoding']

	def process(self, context, event):
		assert isinstance(event, dict)
		return json.dumps(event).encode(self.Encoding)
