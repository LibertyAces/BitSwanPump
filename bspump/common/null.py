from ..abc.sink import Sink


class NullSink(Sink):

	def process(self, context, event):
		pass
