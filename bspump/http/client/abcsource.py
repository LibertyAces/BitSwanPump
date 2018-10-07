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


	def __init__(self, app, pipeline, id=None, config=None, headers={}):
		super().__init__(app, pipeline, id=id, config=config)
		self.Loop = app.Loop

		self.Method = self.Config['method']
		self.URL = self.Config['url']

		self.Headers = headers.copy()
		
		self.SSL = None
		# SSL validation mode (see aiohttp documentation for more details)
		# - None for default SSL check (ssl.create_default_context() is used),
		# - False for skip SSL certificate validation
		# - aiohttp.Fingerprint for fingerprint validation
		# - ssl.SSLContext for custom SSL certificate validation.


	async def main(self):
		async with aiohttp.ClientSession(loop=self.Loop) as session:
			await super().main(session)


	async def cycle(self, session):
		async with session.request(
				self.Method,
				self.URL,
				headers = self.Headers if len(self.Headers) > 0 else None,
				ssl = self.SSL,
			) as response:
			await self.read(response)


	@abc.abstractmethod
	async def read(self, response):
		'''
		Override this method to implement your File Source.
		`f` is an opened file object.
		'''
		raise NotImplemented()

