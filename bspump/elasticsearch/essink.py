import logging
import json
import asyncio

import aiohttp
import asab
import bspump

###

L = logging.getLogger(__name__)

###


asab.Config.add_defaults({
	'elasticsearch': {
		'url': "http://localhost:9200/",
		'bulk_out_max_size': 1,
		'rollover_mechanism': "time_based", 
		'timeout': 300,
	}
})

class ElasticSearchDriver(object):

	def __init__(self, app):
		self.output_queue = asyncio.Queue(maxsize=1000, loop=app.Loop)
		self.url = asab.Config['elasticsearch']['url'].strip()
		if self.url[-1] != '/': self.url += '/'
		self.url_bulk = self.url + '_bulk'

		self.bulk_out_max_size = int(asab.Config['elasticsearch']['bulk_out_max_size'])
		self.bulk_out = ""

		self.timeout = float(asab.Config['elasticsearch']['timeout'])
		self.rollover_type = asab.Config['elasticsearch']['rollover_mechanism']
		#self.max_index_size = int(asab.Config['elasticsearch']['max_index_size'])

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
			#TODO: Add this event to metrics
			return

		#TODO: Add this event to metrics
		self.output_queue.put_nowait(self.bulk_out)
		self.bulk_out = ""


	async def _submit(self, future):
		try:
			while True:
				bulk_out = await self.output_queue.get()
				async with aiohttp.ClientSession() as session:
					async with session.post(self.url_bulk, data=bulk_out, headers={'Content-Type': 'application/json'}, timeout=self.timeout) as resp:
						if resp.status != 200:
							resp_body = await resp.text()
							L.error("Failed to insert document into ElasticSearch status:{} body:{}".format(resp.status, resp_body))
							raise RuntimeError("Failed to insert document into ElasticSearch")

						else:
							resp_body = await resp.text()
							respj = json.loads(resp_body)
							if respj.get('errors', True) != False:
								#TODO: Iterate thru respj['items'] and display only status != 201 items in L.error()
								L.error("Failed to insert document into ElasticSearch status:{} body:{}".format(resp.status, resp_body))
								raise RuntimeError("Failed to insert document into ElasticSearch")

					break
		except:
			L.exception("Error in ElasticSearch driver")
			raise

		future.set_result("done")


class ElasticSearchSink(bspump.Sink):

	def __init__(self, app, pipeline, driver, es_type="xdr", es_index="index"):
		super().__init__(app, pipeline)
		self.es_index = es_index
		self.es_type = es_type
		app.PubSub.subscribe("onTick", self.refresh_index())
		self._driver = driver

	def refresh_index(self):
		pass

	def process(self, event):
		data = '{{"index": {{ "_index": "{}", "_type": "{}" }}\n{}\n'.format(self.es_index, self.es_type, json.dumps(event))
		self._driver.consume(data)



	#TODO: implement index update
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
