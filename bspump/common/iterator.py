import logging
import collections.abc

from ..abc.source import TriggerSource
from ..abc.generator import Generator

#

L = logging.getLogger(__name__)

#

class IteratorSource(TriggerSource):

	def __init__(self, app, pipeline, iterator:collections.abc.Iterator, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Iterator = iterator


	async def cycle(self, *args, **kwags):
		for event in self.Iterator():
			await self.process(event)


class IteratorGenerator(Generator):

	async def generate(self, context, event, depth):
		for item in event:
			await self.Pipeline.inject(context, item, depth)
