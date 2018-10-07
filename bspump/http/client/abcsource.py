import abc
import re
import logging
import asyncio
import aiohttp
from ...abc.source import TriggerSource

#

L = logging.getLogger(__name__)

#

class HTTPABCClientSource(TriggerSource):


	ConfigDefaults = {
		'method': 'GET',
		'url': 'http://example.com/',
		'response_code': '200', # Specify an expected response status code, more values are accepted ("200, 300 301")
		'max_failed_retries': 3,
		'fail_chilldown': 30, # If there is an incorrect response, chilldown for X seconds
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

		self.FailedResponses = 0
		self.MaxFailedResponses = int(self.Config.get('max_failed_retries'))
		self.FailChilldown = float(self.Config.get('fail_chilldown'))
		try:
			self.ResponseCodes = frozenset(map(int, re.findall(r"\d+", self.Config.get('response_code'))))
		except:
			L.error("Failed to parse 'response_code' configuration value")
			raise



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
			if response.status not in self.ResponseCodes:
				self.FailedResponses += 1
				if self.FailedResponses < self.MaxFailedResponses:
					L.warn("Received an incorrect response status code {} from '{}', will retry ({}/{}) in {:0.0f} sec".format(response.status, self.URL, self.FailedResponses, self.MaxFailedResponses, self.FailChilldown))
					self.Pipeline.MetricsCounter.add('warning', 1)
					await asyncio.sleep(self.FailChilldown)
					return
				else:
					t = await response.text()
					if len(t) > 1000: t = t[:1000] + '...'
					L.error("Last failed response (response status code {}):\n{}".format(response.status, t))
					raise RuntimeError("Recevied {} failed responses from '{}', last response status code: {}".format(self.FailedResponses, self.URL, response.status))
			else:
				self.FailedResponses = 0 # Reset the counter
			await self.read(response)


	@abc.abstractmethod
	async def read(self, response):
		'''
		Override this method to implement your HTTP Source.
		'''
		raise NotImplemented()

