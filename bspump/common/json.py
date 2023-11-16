import json
import cysimdjson
from ..abc.processor import Processor


class CySimdJsonParser(Processor):
	'''
	Fast JSON parser. Expects json bytes represented as bytes as input
	Based on https://github.com/TeskaLabs/cysimdjson

	|

	'''

	def __init__(self, app, pipeline, id=None, config=None):
		"""
		Description: .

		|

		"""
		super().__init__(app, pipeline, id, config)
		self._parser = cysimdjson.JSONParser()

	def process(self, context, event: bytes):
		"""
		Description:

		:return: self._parser.parse(event)

		|

		"""
		return self._parser.parse(event)


class StdDictToJsonParser(Processor):

	def process(self, context, event):
		"""
		Description:

		:return: ?

		|

		"""
		return json.dumps(event)


class StdJsonToDictParser(Processor):


	def process(self, context, event):
		"""
		Description:

		:return: ???

		|

		"""
		return json.loads(event)


class DictToJsonBytesParser(Processor):
	"""
	DictToJsonBytesParser transforms a dictionary to JSON-string encoded in bytes.
	The encoding charset can be specified in the configuration in `encoding` field.

	|

	"""
	ConfigDefaults = {
		'encoding': 'utf-8',
	}

	def __init__(self, app, pipeline, id=None, config=None):
		"""
		Description: ..

		|

		"""
		super().__init__(app, pipeline, id, config)
		self.Encoding = self.Config['encoding']

	def process(self, context, event):
		"""
		Description:

		:return: ??

		|

		"""
		assert isinstance(event, dict)
		return json.dumps(event).encode(self.Encoding)
