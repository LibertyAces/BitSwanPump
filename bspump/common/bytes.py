from ..abc.processor import Processor


class StringToBytesParser(Processor):
	"""
	Description:

	|
	** Default Config **

	encoding : utf-8

	"""

	ConfigDefaults = {
		'encoding': 'utf-8',
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		self.Encoding = self.Config['encoding']

	def process(self, context, event):
		"""
		Description:

		:return: event.decode(self.Encoding)

		|

		"""
		assert isinstance(event, str)
		return event.encode(self.Encoding)


class BytesToStringParser(Processor):

	ConfigDefaults = {
		'encoding': 'utf-8',
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		self.Encoding = self.Config['encoding']

	def process(self, context, event):
		"""
		Description:

		:return: event.decode(self.Encoding)

		|

		"""
		assert isinstance(event, bytes)
		return event.decode(self.Encoding)
