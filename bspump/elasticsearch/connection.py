import asyncio
import json
import logging
import random
import re

import aiohttp

from ..abc.connection import Connection

#

L = logging.getLogger(__name__)

#


class ElasticSearchConnection(Connection):
	"""

	ElasticSearchConnection allows your ES source, sink or lookup to connect to ElasticSearch instance

	usage:

.. code:: python


	# adding connection to PumpService
	svc = app.get_service("bspump.PumpService")
	svc.add_connection(
		bspump.elasticsearch.ElasticSearchConnection(app, "ESConnection")
	)

.. code:: python

	# pass connection name ("ESConnection" in our example) to relevant BSPump's object:

	self.build(
			bspump.kafka.KafkaSource(app, self, "KafkaConnection"),
			bspump.elasticsearch.ElasticSearchSink(app, self, "ESConnection")
	)

	"""

	ConfigDefaults = {
		'url': 'http://localhost:9200/',  # Could be multi-URL. Each URL should be separated by ';' to a node in ElasticSearch cluster
		'username': '',
		'password': '',
		'loader_per_url': 4,  # Number of parael loaders per URL
		'output_queue_max_size': 10,
		'bulk_out_max_size': 1024 * 1024,
		'timeout': 300,
		'allowed_bulk_response_codes': '201',
	}

	def __init__(self, app, id=None, config=None):
		super().__init__(app, id=id, config=config)

		self._output_queue_max_size = int(self.Config['output_queue_max_size'])
		self._output_queue = asyncio.Queue(loop=app.Loop)

		username = self.Config.get('username')
		password = self.Config.get('password')

		if username == '':
			self._auth = None
		else:
			self._auth = aiohttp.BasicAuth(login=username, password=password)

		# Contains URLs of each node in the cluster
		self.node_urls = []
		for url in self.Config['url'].split(';'):
			url = url.strip()
			if len(url) == 0:
				continue
			if url[-1] != '/':
				url += '/'
			self.node_urls.append(url)

		self._loader_per_url = int(self.Config['loader_per_url'])

		self._bulk_out_max_size = int(self.Config['bulk_out_max_size'])
		self._bulk_out = ""
		self._started = True

		self._timeout = float(self.Config['timeout'])

		self.Loop = app.Loop

		self.PubSub = app.PubSub
		self.PubSub.subscribe("Application.run!", self._start)
		self.PubSub.subscribe("Application.exit!", self._on_exit)

		self.AllowedBulkResponseCodes = frozenset(
			[int(x) for x in re.findall(r"[0-9]+", self.Config['allowed_bulk_response_codes'])]
		)

		self._futures = []
		for url in self.node_urls:
			for i in range(self._loader_per_url):
				self._futures.append((url + '_bulk', None))


	def get_url(self):
		return random.choice(self.node_urls)

	def consume(self, data):
		self._bulk_out += data

		if len(self._bulk_out) > self._bulk_out_max_size:
			self.flush()


	def get_session(self):
		return aiohttp.ClientSession(auth=self._auth, loop=self.Loop)

	def _start(self, event_type):
		self.PubSub.subscribe("Application.tick/10!", self._on_tick)
		self._on_tick("simulated!")

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
				except Exception:
					L.exception("ElasticSearch error observed, restoring the order")

				self._futures[i] = (url, None)

			# 2) Start _loader() futures that are exitted
			if self._started:
				url, future = self._futures[i]
				if future is None:
					future = asyncio.ensure_future(self._loader(url), loop=self.Loop)
					self._futures[i] = (url, future)

		self.flush()


	def flush(self):
		if len(self._bulk_out) == 0:
			# TODO: Add this event to metrics
			return

		# TODO: Add this event to metrics
		assert(self._bulk_out is not None)
		self._output_queue.put_nowait(self._bulk_out)
		self._bulk_out = ""

		# Signalize need for throttling
		if self._output_queue.qsize() == self._output_queue_max_size:
			self.PubSub.publish("ElasticSearchConnection.pause!", self)


	async def _loader(self, url):
		async with self.get_session() as session:
			while self._started:
				bulk_out = await self._output_queue.get()
				if bulk_out is None:
					break

				if self._output_queue.qsize() == self._output_queue_max_size - 1:
					self.PubSub.publish("ElasticSearchConnection.unpause!", self, asynchronously=True)

				# TODO: if exception happens, save bulk_out back to queue for a future resend (don't forget throttling)

				L.debug("Sending bulk request (size: {}) to {}".format(len(bulk_out), url))

				async with session.post(url, data=bulk_out, headers={'Content-Type': 'application/json'}, timeout=self._timeout) as resp:
					if resp.status != 200:
						resp_body = await resp.text()
						L.error("Failed to insert document into ElasticSearch status:{} body:{}".format(resp.status, resp_body))
						raise RuntimeError("Failed to insert document into ElasticSearch")

					else:
						resp_body = await resp.text()
						respj = json.loads(resp_body)
						if respj.get('errors', True) is not False:
							error_level = 0
							for item in respj['items']:
								# TODO: item['index']['status']: add metrics counter for status code
								if item['index']['status'] not in self.AllowedBulkResponseCodes:
									if error_level == 0:
										L.error("Failed to insert bulk into ElasticSearch status: {}".format(resp.status))
									error_level += 1
									L.error(" - {} Failed document detail: '{}'".format(item['index']['status'], item))
							if error_level > 0:
								raise RuntimeError("Failed to insert document into ElasticSearch")

						L.debug("Bulk POST finished successfully")
