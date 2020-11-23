try:
	import orjson
except ModuleNotFoundError:
	pass

# IMPORTANT: This module is obsolete, not supported and will be removed in a future

from ..abc.processor import Processor


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
		return orjson.dumps(event)


class JsonBytesToDictParser(Processor):
	"""
	JsonBytesToDictParser transforms a JSON-string encoded in bytes to a dictionary.
	The encoding charset can be specified in the configuration in `encoding` field.
	"""

	ConfigDefaults = {
		'encoding': 'utf-8',
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		self.Encoding = self.Config['encoding']

	def process(self, context, event):
		assert isinstance(event, bytes)
		return orjson.loads(event)
