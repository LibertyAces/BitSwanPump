import abc
import logging
from ..abc.processor import Processor


###

L = logging.getLogger(__name__)

###

class Analyzer(Processor):
	'''
	This is analyzer interface
	'''

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

	## Implementation interface
	@abc.abstractmethod
	def predicate(self, event):
		raise NotImplemented("")

	@abc.abstractmethod
	def analyze(self):
		raise NotImplemented("")

	@abc.abstractmethod
	def evaluate(self, event):
		raise NotImplemented("")

	def process(self, context, event):
		if self.predicate(event):
			self.evaluate(event)

		return event

