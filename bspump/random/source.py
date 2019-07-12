import logging
import random
from ..abc.source import TriggerSource

#

L = logging.getLogger(__name__)

#

class RandomSource(TriggerSource):
	'''
		`RandomSource` is mostly meant for testing. It
		generates n (specified in `Config` as `number`, default is 1000) events per trigger fire.
		Those event contain only one field with the name from `Config['field']`, default is "id".
		There can be 2 options of usage:
		a) User provides `choice` as an array of values to choice randomly and assigned to field;
		b) The random integer between `Config['lower_bound']` and `Config['upper_bound']` is generated with
		`Config['prefix']` and assigned.
	'''

	ConfigDefaults = {
		'field': 'id',
		'prefix': 'id_',
		'number': 1000,
		'lower_bound': 0,
		'upper_bound': 1000,
	}
	
	def __init__(self, app, pipeline, choice=None, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Field = self.Config['field']
		self.Prefix = self.Config['prefix']
		self.Number = int(self.Config['number'])
		self.LowerBound = int(self.Config['lower_bound'])
		self.UpperBound = int(self.Config['upper_bound'])
		self.Choice = None
		if choice is not None:
			self.Choice = choice


	def generate_random(self, event):
		'''
			Override this method to generate differently
		'''
		if self.Choice:
			event[self.Field] = random.choice(self.Choice)
		else:
			n = random.randint(self.LowerBound, self.UpperBound)
			event[self.Field] = "{}{}".format(self.Prefix, n)


	async def cycle(self):
		try:
			for i in range(0, self.Number):
				event = {}
				self.generate_random(event)
				await self.process(event)
		
		except BaseException as e:
			L.exception("Unexpected error generating random")

