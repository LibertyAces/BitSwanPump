import pprint
from .. import Sink

class PrintSink(Sink):

	def process(self, data):
		print(data)


class PPrintSink(Sink):

	def process(self, data):
		pprint.pprint(data)
