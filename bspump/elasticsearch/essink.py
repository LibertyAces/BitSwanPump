import asab
import logging
import bspump
import asyncio
import aiohttp
import json


###

L = logging.getLogger(__name__)

###

class ElasticSearchDriver(object):

	def __init__(self, app):
		self.output_queue = asyncio.Queue(maxsize=1000, loop=app.Loop)

		self.url = Config['elasticsearch']['url'].strip()
		if self.url[-1] != '/': self.url += '/'
		self.url_bulk = self.url + '_bulk'

		self.bulk_out_max_size = int(Config['elasticsearch']['bulk_out_max_size'])
		self.bulk_out = ""

		self.timeout = float(Config['elasticsearch']['timeout'])
		self.rollover_type = Config['elasticsearch']['rollover_mechanism']
		self.max_index_size = int(Config['elasticsearch']['max_index_size'])

		app.PubSub.subscribe("Application.tick!", self.flush)
		app.PubSub.subscribe("Application.exit!", self.flush)

		future = asyncio.Future()
		asyncio.ensure_future(self._submit(future))

	def consume(self, data):
		self.bulk_out += data

		if len(self.bulk_out) > self.bulk_out_max_size:
			self.flush()

	def flush(self, event_name=None):
		if len(self.bulk_out) == 0:
			return

		self.output_queue.put_nowait(self.bulk_out)
		self.bulk_out = ""

	async def _submit(self, future):
		while True:
			bulk_out = await self.output_queue.get()
			async with aiohttp.ClientSession() as session:
				async with session.post('', data=bulk_out) as resp:
					if resp.status_code != 200:
						L.error("Failed to insert document into ElasticSearch status:{} body:{}".format(resp.status_code, resp.text))
						raise RuntimeError("Failed to insert document into ElasticSearch")

					else:
						respj = json.loads(resp.text)
						if respj.get('errors', True) != False:
							L.error("Failed to insert document into ElasticSearch status:{} body:{}".format(resp.status_code, resp.text))
							raise RuntimeError("Failed to insert document into ElasticSearch")

				break
		future.set_result("done")

	def update_index(self, es_type, version, es_index_period, orig_index=None):		
		if self.rollover_type == 'index_size_based':
			return self.index_size_based_update(es_type, version, es_index_period, orig_index)
		elif self.rollover_type == 'time_based':
			return self.time_based_update(es_type, version, es_index_period)
		else: 
			L.error("Invalid rollover mechanism: '{}'. Allowed values are 'index_size_based' or 'time_based'.").format(self.rollover_type)
			raise RuntimeError("Index rollover failed.")

	def _generate_es_index(self, es_type, version, seqno):
		return "{}_{}{:05}".format(es_type, version, seqno)

	def index_size_based_update(self, es_type, version, es_index_period, orig_index):
		
		if orig_index is not None:
			# Get actual size of the currently active index
			url_get_index_size = self.url + '{}/_stats/store'.format(orig_index)
			stats = self.session.get(url_get_index_size, timeout=self.timeout)
			data = stats.json()

			if data.get('_all') is None:
				current_index_size = 0
			else:
				current_index_size = data['_all']['primaries']['store']['size_in_bytes']
		else:
			current_index_size = 0

		if (orig_index is None) or (current_index_size >= self.max_index_size):
			# Roll over to a new index
			seqno = int((time.time() - 1500000000) / es_index_period)
			new_es_index = self._generate_es_index(es_type, version, seqno)

			if new_es_index == orig_index:
				L.warning("ElasticSearch index name update resulted in original name, decrease es_index_period value.")

			return new_es_index 		

		else:
			return orig_index

	def time_based_update(self, es_type, version, es_index_period):
		seqno = int((time.time() - 1500000000) / es_index_period)
		return self._generate_es_index(es_type, version, seqno)

	def parse_index_period(self, value):
		if value == 'd': return 60*60*24 # 1 day
		elif value == 'w': return 60*60*24*7 # 7 days
		elif value == 'm': return 60*60*24*28 # 28 days

		return int(value) # Otherwise use value in seconds


class ElasticSearchSink(bspump.Sink):

	def __init__(self, app, pipeline, driver):
		super().__init__(app, pipeline)
		self._driver = driver

	def process(self, event):
		data = '{{"index": {{ "_index": "{}", "_type": "{}" }}\n{}\n'.format(es_index, es_type, json.dumps(obj))
		self._driver.consume(data)

