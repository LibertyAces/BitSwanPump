from ..abc.processor import Processor
import random


class RandomEnricher(Processor):
	'''
		`RandomEnricher` is mostly meant for testing.
		It adds to event only one field with the name from `Config['field']`, default is "id".
		There can be 2 options of usage:
		a) User provides `choice` as an array of values to choice randomly and assigned to field;
		b) The random integer between `Config['lower_bound']` and `Config['upper_bound']`.
	'''

	ConfigDefaults = {
		'field': 'enriched_field',
		'lower_bound': 0,
		'upper_bound': 1000,
	}

	def __init__(self, app, pipeline, choice=None, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Field = self.Config['field']
		self.LowerBound = int(self.Config['lower_bound'])
		self.UpperBound = int(self.Config['upper_bound'])
		self.Choice = None
		if choice is not None:
			self.Choice = choice


	def generate_random(self, context, event):
		'''
			Override this method to generate differently
		'''
		if self.Choice is not None:
			event[self.Field] = random.choice(self.Choice)
		else:
			n = random.randint(self.LowerBound, self.UpperBound)
			event[self.Field] = n


	def process(self, context, event):
		self.generate_random(context, event)
		return event
