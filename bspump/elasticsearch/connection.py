import asyncio
import logging
import random

import orjson
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
		'bulk_out_max_size': 2 * 1024 * 1024,
		'timeout': 300,
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
		self._bulks = {}

		self._timeout = float(self.Config['timeout'])
		self._started = True

		self.Loop = app.Loop

		self.PubSub = app.PubSub
		self.PubSub.subscribe("Application.run!", self._start)
		self.PubSub.subscribe("Application.exit!", self._on_exit)

		self._futures = []
		for url in self.node_urls:
			for i in range(self._loader_per_url):
				self._futures.append((url, None))


	def get_url(self):
		return random.choice(self.node_urls)


	def get_session(self):
		return aiohttp.ClientSession(auth=self._auth, loop=self.Loop)


	def consume(self, index, _id, data):
		bulk = self._bulks.get(index)
		if bulk is None:
			bulk = ElasticSearchBulk(index, self._bulk_out_max_size)
			self._bulks[index] = bulk

		if bulk.consume(_id, data):
			# Bulk is ready, schedule to be send
			del self._bulks[index]
			self._output_queue.put_nowait(bulk)

			# Signalize need for throttling
			if self._output_queue.qsize() == self._output_queue_max_size:
				self.PubSub.publish("ElasticSearchConnection.pause!", self)


	def _start(self, event_type):
		self.PubSub.subscribe("Application.tick!", self._on_tick)
		self._on_tick("simulated!")


	async def _on_exit(self, event_name):
		self._started = False
		self.flush(forced=True)

		# Wait till the _loader() terminates (one after another)
		pending = [item[1] for item in self._futures]
		self._futures = []
		while len(pending) > 0:
			# By sending None via queue, we signalize end of life
			await self._output_queue.put(None)
			done, pending = await asyncio.wait(pending, return_when=asyncio.ALL_COMPLETED)


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
					future = asyncio.ensure_future(self._loader(url))
					self._futures[i] = (url, future)

		self.flush()


	def flush(self, forced=False):
		aged = []
		for index, bulk in self._bulks.items():
			bulk.Aging += 1
			if (bulk.Aging >= 2) or forced:
				aged.append(index)

		for index in aged:
			bulk = self._bulks.pop(index)
			self._output_queue.put_nowait(bulk)

			# Signalize need for throttling
			if self._output_queue.qsize() == self._output_queue_max_size:
				self.PubSub.publish("ElasticSearchConnection.pause!", self)


	async def _loader(self, url):
		async with self.get_session() as session:
			while self._started:
				bulk = await self._output_queue.get()
				if bulk is None:
					break

				if self._output_queue.qsize() == self._output_queue_max_size - 1:
					self.PubSub.publish("ElasticSearchConnection.unpause!", self, asynchronously=True)

				await bulk.upload(url, session, self._timeout)


class ElasticSearchBulk(object):


	def __init__(self, index, max_size):
		self.Index = index
		self.Aging = 0
		self.Capacity = max_size
		self.Items = []


	def consume(self, _id, data):
		self.Items.append((_id, data))
		self.Capacity -= len(data)
		self.Aging = 0
		return self.Capacity <= 0


	async def upload(self, url, session, timeout):
		if len(self.Items) == 0:
			return

		url = url + '{}/_bulk?filter_path=items.*.error'.format(self.Index)

		async with session.post(
			url,
			data=self._data_feeder(),
			headers={
				'Content-Type': 'application/json'
			},
			timeout=timeout,
		) as resp:

			# Obtain the response from ElasticSearch,
			# which should always be a json
			resp_body = await resp.json()

			if resp.status == 200:

				# Check that all documents were successfully inserted to ElasticSearch
				# Since 'filter_path=items.*.error' is set, only error items are returned
				items = resp_body.get("items")
				if items is None:
					return

				# Some of the documents were not inserted properly,
				# usually because of attributes mismatch, see:
				# https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html
				for item in items:
					L.error("Failed to insert document into ElasticSearch: '{}'".format(
						str(item)
					))

			else:

				# An ElasticSearch error occurred while inserting documents
				L.error("Failed to insert document into ElasticSearch status:{} body:{}".format(
					resp.status,
					resp_body
				))
				raise RuntimeError("Failed to insert document into ElasticSearch")


	async def _data_feeder(self):
		for _id, data in self.Items:
			yield b'{"create":{}}\n' if _id is None else orjson.dumps({"index": {"_id": _id}}, option=orjson.OPT_APPEND_NEWLINE)
			yield data
