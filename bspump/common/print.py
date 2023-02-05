import sys
import pprint
from ..abc.sink import Sink
from ..abc.processor import Processor


class PrintSink(Sink):
	"""
	Description:

	|

	"""

	def __init__(self, app, pipeline, id=None, config=None, stream=None):
		"""
		Description:

		|

		"""
		super().__init__(app, pipeline, id, config)
		self.Stream = stream if stream is not None else sys.stdout

	def process(self, context, event):
		"""
		Description:

		|

		"""
		print(event, file=self.Stream)


class PPrintSink(Sink):
	"""
	Description:

	|

	"""

	def __init__(self, app, pipeline, id=None, config=None, stream=None):
		"""
		Description:

		|

		"""
		super().__init__(app, pipeline, id, config)
		self.Stream = stream if stream is not None else sys.stdout

	def process(self, context, event):
		"""
		Description:

		|

		"""
		pprint.pprint(event, stream=self.Stream)


class PrintProcessor(Processor):
	"""
	Description:

	|

	"""

	def __init__(self, app, pipeline, id=None, config=None, stream=None):
		"""
		Description:

		|

		"""
		super().__init__(app, pipeline, id, config)
		self.Stream = stream if stream is not None else sys.stdout

	def process(self, context, event):
		"""
		Description:

		|

		:return: event
		"""
		print(event, file=self.Stream)
		return event


class PPrintProcessor(Processor):
	"""
	Description:

	|

	"""

	def __init__(self, app, pipeline, id=None, config=None, stream=None):
		"""
		Description:

		|

		"""
		super().__init__(app, pipeline, id, config)
		self.Stream = stream if stream is not None else sys.stdout

	def process(self, context, event):
		"""
		Description:

		|

		:return: event
		"""
		pprint.pprint(event, stream=self.Stream)
		return event


class PrintContextProcessor(Processor):
	"""
	Description:

	|

	"""

	def __init__(self, app, pipeline, id=None, config=None, stream=None):
		"""
		Description:

		|

		"""
		super().__init__(app, pipeline, id, config)
		self.Stream = stream if stream is not None else sys.stdout

	def process(self, context, event):
		"""
		Description:

		|
		
		:return: event
		
		"""

		print(context, file=self.Stream)
		return event


class PPrintContextProcessor(Processor):
	"""
	Description:

	|

	"""

	def __init__(self, app, pipeline, id=None, config=None, stream=None):
		"""
		Description:

		|

		"""
		super().__init__(app, pipeline, id, config)
		self.Stream = stream if stream is not None else sys.stdout

	def process(self, context, event):
		"""
		Description:

		|

		:return: event
		"""
		pprint.pprint(context, stream=self.Stream)
		return event
