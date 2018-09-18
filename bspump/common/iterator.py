import logging
from ..abc.source import TriggerSource
#

L = logging.getLogger(__name__)

#

class IteratorSource(TriggerSource):

	def __init__(self, app, pipeline, iterator, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Iterator = iterator


	async def cycle(self, *args, **kwags):
		for event in self.Iterator():
			await self.process(event)
