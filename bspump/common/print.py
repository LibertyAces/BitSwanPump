import sys
import pprint
from ..abc.sink import Sink
from ..abc.processor import Processor


class PrintSink(Sink):

	def __init__(self, app, pipeline, id=None, config=None, stream=None):
		super().__init__(app, pipeline, id, config)
		self.Stream = stream if stream is not None else sys.stdout

	def process(self, context, event):
		print(event, file=self.Stream)


class PPrintSink(Sink):

	def __init__(self, app, pipeline, id=None, config=None, stream=None):
		super().__init__(app, pipeline, id, config)
		self.Stream = stream if stream is not None else sys.stdout

	def process(self, context, event):
		pprint.pprint(event, stream=self.Stream)


class PrintProcessor(Processor):

	def __init__(self, app, pipeline, id=None, config=None, stream=None):
		super().__init__(app, pipeline, id, config)
		self.Stream = stream if stream is not None else sys.stdout

	def process(self, context, event):
		print(event, file=self.Stream)
		return event


class PPrintProcessor(Processor):

	def __init__(self, app, pipeline, id=None, config=None, stream=None):
		super().__init__(app, pipeline, id, config)
		self.Stream = stream if stream is not None else sys.stdout

	def process(self, context, event):
		pprint.pprint(event, stream=self.Stream)
		return event


class PrintContextProcessor(Processor):

	def __init__(self, app, pipeline, id=None, config=None, stream=None):
		super().__init__(app, pipeline, id, config)
		self.Stream = stream if stream is not None else sys.stdout

	def process(self, context, event):
		print(context, file=self.Stream)
		return event


class PPrintContextProcessor(Processor):

	def __init__(self, app, pipeline, id=None, config=None, stream=None):
		super().__init__(app, pipeline, id, config)
		self.Stream = stream if stream is not None else sys.stdout

	def process(self, context, event):
		pprint.pprint(context, stream=self.Stream)
		return event
