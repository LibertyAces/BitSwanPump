import abc
import logging
import asyncio
import aiohttp
from ...abc.source import TriggerSource

#

L = logging.getLogger(__file__)

#

class HTTPABCClientSource(TriggerSource):


	ConfigDefaults = {
		'method': 'GET',
		'url': 'http://example.com/',
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Loop = app.Loop

		self._request_method = self.Config['method']
		self._request_url = self.Config['url']


	async def main(self):
		async with aiohttp.ClientSession(loop=self.Loop) as session:
			await super().main(session)


	async def cycle(self, session):
		async with session.request(self._request_method, self._request_url) as response:
			await self.read(response)


	@abc.abstractmethod
	async def read(self, response):
		'''
		Override this method to implement your File Source.
		`f` is an opened file object.
		'''
		raise NotImplemented()

