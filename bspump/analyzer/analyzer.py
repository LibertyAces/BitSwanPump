import abc
import logging
from ..abc.processor import Processor


###

L = logging.getLogger(__name__)

###

class Analyzer(Processor):
	'''
		This is general analyzer interface, which can be the basement of different analyzers. 
	'''

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

	## Implementation interface
	def analyze(self):
		'''
			The main function, which runs through the analyzed object.
			Specific for each analyzer.
		'''
		pass


	def evaluate(self, context, event):
		'''
			The function which records the information from the event into the analyzed object.
			Specific for each analyzer.
		'''
		pass


	def predicate(self, context, event):
		'''
			This function is meant to check, if the event is worth to process.
			If it is, should return True.
			Specific for each analyzer, but default one always returns True.
		'''
		return True

	def process(self, context, event):
		'''
			The event passes through `process(context, event)` unchanged.
			Meanwhile it is evaluated. 
		'''
		if self.predicate(context, event):
			self.evaluate(context, event)

		return event

