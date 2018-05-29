import pprint
from ..abc.sink import Sink
from ..abc.processor import Processor

class PrintSink(Sink):

	def process(self, context, event):
		print(event)


class PPrintSink(Sink):

	def process(self, context, event):
		pprint.pprint(event)


class PrintProcessor(Processor):

	def process(self, context, event):
		print(event)
		return event


class PPrintProcessor(Processor):

	def process(self, context, event):
		pprint.pprint(event)
		return event


class PrintContextProcessor(Processor):

	def process(self, context, event):
		print(context)
		return event

class PPrintContextProcessor(Processor):

	def process(self, context, event):
		pprint.pprint(context)
		return event
