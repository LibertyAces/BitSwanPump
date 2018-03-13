import asyncio
import aiohttp
import logging
import pprint
import json

from asab import Config

from ..abc.connection import Connection

#

L = logging.getLogger(__name__)

#

class ElasticSearchConnection(Connection):


	ConfigDefaults = {
		#TODO: Support multiple url (cluster), select randomly the one used, iterate to a next one if there is a connection error
		'url': 'http://localhost:9200/',
		'output_queue_max_size': 10,
		'bulk_out_max_size': 1024*1024,
		'timeout': 300,
	}


	def __init__(self, app, connection_id, config=None):
		super().__init__(app, connection_id, config=config)

		self._output_queue = asyncio.Queue(maxsize=int(self.Config['output_queue_max_size']), loop=app.Loop)
		self.url = self.Config['url'].strip()
		if self.url[-1] != '/': self.url += '/'
		self._url_bulk = self.url + '_bulk'

		self._bulk_out_max_size = int(self.Config['bulk_out_max_size'])
		self._bulk_out = ""
		self._started = True

		self._timeout = float(self.Config['timeout'])

		app.PubSub.subscribe("Application.tick!/10", self._on_tick)
		app.PubSub.subscribe("Application.exit!", self._on_exit)

		self._future = asyncio.ensure_future(self._submit())


	def consume(self, data):
		self._bulk_out += data

		if len(self._bulk_out) > self._bulk_out_max_size:
			self.flush()


	async def _on_exit(self, event_name):
		self._started = False
		self.flush()
		await self._output_queue.put(None) # By sending None via queue, we signalize end of life
		await self._future # Wait till the _submit() terminates


	def _on_tick(self, event_name):
		if self._started and self._future.done():
			# Ups, _submit() task crashed during runtime, we need to restart it
			try:
				r = self._future.result()
				# This error should never happen
				L.error("ElasticSearch error observed, returned: '{}' (should be None)".format(r))
			except:
				L.exception("ElasticSearch error observed, restoring the order")

			# Start _submit() future again
			self._future = asyncio.ensure_future(self._submit())			

		self.flush()


	def flush(self):
		if len(self._bulk_out) == 0:
			#TODO: Add this event to metrics
			return

		#TODO: Add this event to metrics
		assert(self._bulk_out is not None)
		self._output_queue.put_nowait(self._bulk_out)
		self._bulk_out = ""


	async def _submit(self):
		while self._started:
			bulk_out = await self._output_queue.get()
			if bulk_out is None:
				break

			#TODO: if exception happends, save bulk_out somewhere for a future resend

			async with aiohttp.ClientSession() as session:
				async with session.post(self._url_bulk, data=bulk_out, headers={'Content-Type': 'application/json'}, timeout=self._timeout) as resp:
					if resp.status != 200:
						resp_body = await resp.text()
						L.error("Failed to insert document into ElasticSearch status:{} body:{}".format(resp.status, resp_body))
						raise RuntimeError("Failed to insert document into ElasticSearch")

					else:
						resp_body = await resp.text()
						respj = json.loads(resp_body)
						pprint.pprint(respj)
						if respj.get('errors', True) != False:
							#TODO: Iterate thru respj['items'] and display only status != 201 items in L.error()
							L.error("Failed to insert document into ElasticSearch status:{} body:{}".format(resp.status, resp_body))
							raise RuntimeError("Failed to insert document into ElasticSearch")
