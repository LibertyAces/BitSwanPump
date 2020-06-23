import logging
import asyncio
import random
from ..abc.source import TriggerSource


L = logging.getLogger(__name__)


class RandomSource(TriggerSource):
	'''
		`RandomSource` is mostly meant for testing. It
		generates n (specified in `Config` as `number`, default is 1000) events per trigger fire.

		There can be 2 options of usage:
		a) User provides `choice` as an array of values to choose randomly;
		b) The random integer between `Config['lower_bound']` and `Config['upper_bound']`

		If `field` from `Config` is not an empty string, the random source generates dictionary
		event `{`field`: `generated value`}`. Otherwise it's a random number.
	'''

	ConfigDefaults = {
		'field': '',
		'number': 1000,
		'lower_bound': 0,
		'upper_bound': 1000,
		'event_idle_time': 0.01,
		'events_till_idle': 10000,
	}

	def __init__(self, app, pipeline, choice=None, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Number = int(self.Config['number'])
		self.LowerBound = int(self.Config['lower_bound'])
		self.UpperBound = int(self.Config['upper_bound'])
		self.EventIdleTime = float(self.Config['event_idle_time'])
		self.EventsTillIdle = int(self.Config['events_till_idle'])
		self.EventCounter = 0
		self.Choice = None
		self.Field = None
		if choice is not None:
			self.Choice = choice

		if self.Config['field'] != '':
			self.Field = self.Config['field']


	def generate_random(self):
		'''
			Override this method to generate differently
		'''
		if self.Choice is not None:
			if self.Field is not None:
				return {self.Field : random.choice(self.Choice)}
			
			return random.choice(self.Choice)
		else:
			if self.Field is not None:
				return {self.Field: random.randint(self.LowerBound, self.UpperBound)}

			return random.randint(self.LowerBound, self.UpperBound)


	async def cycle(self):
		for i in range(0, self.Number):
			event = self.generate_random()
			await self.process(event)
			if self.EventCounter >= self.EventsTillIdle:
				await asyncio.sleep(self.EventIdleTime)
				self.EventCounter = 0

			self.EventCounter += 1
