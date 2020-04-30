import logging
from ..abc.source import TriggerSource

L = logging.getLogger(__name__)



class UnitTestSource(TriggerSource):

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Input = []


	async def cycle(self, *args, **kwags):
		try:
			for context, event in self.Input:
				await self.process(event, context=context)
		except:
			L.exception("During unit test")
