import asyncio
import aiohttp
import logging
import json
import random

from asab import Config

from ..abc.connection import Connection

#

L = logging.getLogger(__name__)

#

class ElasticSearchConnection(Connection):


	ConfigDefaults = {
		'url': 'http://localhost:9200/', # Could be multiline, each line is a URL to a node in ElasticSearch cluster
		'loader_per_url': 4, # Number of parael loaders per URL
		'output_queue_max_size': 10,
		'bulk_out_max_size': 1024*1024,
		'timeout': 300,
	}


	def __init__(self, app, connection_id, config=None):
		super().__init__(app, connection_id, config=config)

		self._output_queue_max_size = int(self.Config['output_queue_max_size'])
		self._output_queue = asyncio.Queue(loop=app.Loop)
		
		# Contains URLs of each node in the cluster
		self.node_urls = []
		for url in self.Config['url'].split('\n'):
			url = url.strip()
			if len(url) == 0: continue
			if url[-1] != '/': url += '/'
			self.node_urls.append(url)
 
		self._loader_per_url = int(self.Config['loader_per_url'])

		self._bulk_out_max_size = int(self.Config['bulk_out_max_size'])
		self._bulk_out = ""
		self._started = True

		self._timeout = float(self.Config['timeout'])

		self.Loop = app.Loop

		self.PubSub = app.PubSub
		self.PubSub.subscribe("Application.tick/10!", self._on_tick)
		self.PubSub.subscribe("Application.exit!", self._on_exit)

		self._futures = []
		for url in self.node_urls:
			for i in range(self._loader_per_url):
				self._futures.append((url+'_bulk', None))

		self._on_tick("simulated!")


	def get_url(self):
		return random.choice(self.node_urls)


	def consume(self, data):
		self._bulk_out += data

		if len(self._bulk_out) > self._bulk_out_max_size:
			self.flush()


	async def _on_exit(self, event_name):
		self._started = False
		self.flush()

		# Wait till the _loader() terminates (one after another)
		pending = [item[1] for item in self._futures]
		while len(pending) > 0:
			# By sending None via queue, we signalize end of life
			await self._output_queue.put(None)
			done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)


	def _on_tick(self, event_name):
		for i in range(len(self._futures)):

			# 1) Check for exited futures
			url, future = self._futures[i]
			if future is not None and future.done():
				# Ups, _loader() task crashed during runtime, we need to restart it
				try:
					r = future.result()
					# This error should never happen
					L.error("ElasticSearch error observed, returned: '{}' (should be None)".format(r))
				except:
					L.exception("ElasticSearch error observed, restoring the order")

				self._futures[i] = (url, None)

			# 2) Start _loader() futures that are exitted
			if self._started:
				url, future = self._futures[i]
				if future is None:
					future = asyncio.ensure_future(self._loader(url), loop = self.Loop)			
					self._futures[i] = (url, future)

		self.flush()


	def flush(self):
		if len(self._bulk_out) == 0:
			#TODO: Add this event to metrics
			return

		#TODO: Add this event to metrics
		assert(self._bulk_out is not None)
		self._output_queue.put_nowait(self._bulk_out)
		self._bulk_out = ""

		#Signalize need for throttling
		if self._output_queue.qsize() == self._output_queue_max_size:
			self.PubSub.publish("ElasticSearchConnection.pause!", self)


	async def _loader(self, url):
		async with aiohttp.ClientSession() as session:
			while self._started:
				bulk_out = await self._output_queue.get()
				if bulk_out is None:
					break

				if self._output_queue.qsize() == self._output_queue_max_size - 1:
					self.PubSub.publish("ElasticSearchConnection.unpause!", self, asynchronously=True)

				#TODO: if exception happens, save bulk_out back to queue for a future resend (don't foget throttling)

				L.debug("Sending bulk request (size: {}) to {}".format(len(bulk_out), url))
			
				async with session.post(url, data=bulk_out, headers={'Content-Type': 'application/json'}, timeout=self._timeout) as resp:
					if resp.status != 200:
						resp_body = await resp.text()
						L.error("Failed to insert document into ElasticSearch status:{} body:{}".format(resp.status, resp_body))
						raise RuntimeError("Failed to insert document into ElasticSearch")

					else:
						resp_body = await resp.text()
						respj = json.loads(resp_body)
						if respj.get('errors', True) != False:

							L.error("Failed to insert bulk into ElasticSearch status: {}".format(resp.status))
							for item in respj['items']:
								if item['index']['status'] != 201:
									L.error(" - {} Failed document detail: '{}'".format(item['index']['status'], item))

							raise RuntimeError("Failed to insert document into ElasticSearch")
						else:
							L.debug("Bulk POST finished successfully")
