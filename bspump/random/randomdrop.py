from ..abc.processor import Processor
import random


class RandomDrop(Processor):
	'''
		Simulates random drop of events.
	'''

	ConfigDefaults = {
		"threshold": 0.5,
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Threshold = float(self.Config['threshold'])

	def process(self, context, event):
		if random.random() < self.Threshold:
			return None
		return event
