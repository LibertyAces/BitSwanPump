import pprint
from ..abc.sink import Sink
from ..abc.processor import Processor

class PrintSink(Sink):

	def process(self, event):
		print(event)


class PPrintSink(Sink):

	def process(self, event):
		pprint.pprint(event)


class PrintProcessor(Processor):

	def process(self, event):
		print(event)
		return event


class PPrintProcessor(Processor):

	def process(self, event):
		pprint.pprint(event)
		return event
