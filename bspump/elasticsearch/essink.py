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
		self.output_bucket_max_size = 1000
		self.output_bucket = ""
		self.output_queue = asyncio.Queue(maxsize=1000, loop=app.Loop)

		self.url = asab.Config["elasticsearch"]["url"].strip()
		if self.url[-1] != '/':
			self.url += '/'
		self.url += 'write?db=' + asab.Config["elasticsearch"]["db"]


		app.PubSub.subscribe("Application.tick!", self.flush)
		app.PubSub.subscribe("Application.exit!", self.flush)

		future = asyncio.Future()
		asyncio.ensure_future(self._submit(future))


	def consume(self, data):
		self.output_bucket += data
		if len(self.output_bucket) > self.output_bucket_max_size:
			self.flush()

	def flush(self, event_name=None):
		if len(self.output_bucket) == 0:
			return

		self.output_queue.put_nowait(self.output_bucket)
		self.output_bucket = ""


	async def _submit(self, future):
		while True:
			output_bucket = await self.output_queue.get()
			async with aiohttp.ClientSession() as session:
				async with session.post('', data=output_bucket) as resp:
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


class ElasticSearchSink(bspump.Sink):

	def __init__(self, app, pipeline, driver):
		super().__init__(app, pipeline)
		self._driver = driver

	def process(self, event):
		# Processing data by line
		wire_line = "{},{} {} {}\n".format(
			event['measurement'], event['tag_set'], event['field_set'], int(event['timestamp']))
		self._driver.consume(wire_line)
