import pprint
from .. import Sink

class PrintSink(Sink):

	def process(self, event):
		print(event)


class PPrintSink(Sink):

	def process(self, event):
		pprint.pprint(event)
