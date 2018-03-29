import abc
import logging
import asyncio
import aiohttp
from ... import Source

#

L = logging.getLogger(__file__)

#

class HTTPABCClientSource(Source):


	ConfigDefaults = {
		'method': 'GET',
		'url': 'http://example.com/',
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Loop = app.Loop
		app.PubSub.subscribe("Application.tick/10!", self._on_health_check)
		self._future = None

		self.request_method = self.Config['method']
		self.request_url = self.Config['url']


	@abc.abstractmethod
	async def read(self, response):
		'''
		Override this method to implement your File Source.
		`f` is an opened file object.
		'''
		raise NotImplemented()


	async def start(self):
		self._on_health_check('pipeline.started!')


	def _on_health_check(self, message_type):
		if self._future is not None:
			if not self._future.done():
				# We are still processing a file
				return

			try:
				self._future.result()
			except:
				L.exception("Unexpected error when reading file")

			self._future = None

		assert(self._future is None)

		self._future = asyncio.ensure_future(
			self._fetch(),
			loop=self.Loop
		)


	async def _fetch(self):
		await self.Pipeline.ready()

		try:
			async with aiohttp.ClientSession() as session:
				async with session.request(self.request_method, self.request_url) as response:
					await self.read(response)

		except aiohttp.ClientError as e:
			L.warning("Failed to fetch data from '{}': {}".format(url, e))
