import pprint
from .. import Sink, Processor

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
