import logging
import asyncio
import aiohttp
import json

from asab import Config

from ..abc.connection import Connection


#

L = logging.getLogger(__name__)

#


# TODO: Restructure data: { "measurement": "location", "tag_set": "location=us-midwest", "field_set": "temperature=82", "timestamp": 1465839830100400200 }
class InfluxDBConnection(Connection):

	ConfigDefaults = {
		"url": 'http://localhost:8086/',
		'output_queue_max_size': 10,
		'output_bucket_max_size': 1000,
		'timeout': 30,
		'db': 'mydb' 
	}

	def __init__(self, app, connection_id, config=None):
		super().__init__(app, connection_id, config=config)

		self.url = self.Config["url"].strip()		
		if self.url[-1] != '/':
			self.url += '/'
		
		self.url += 'write?db=' + self.Config["db"]

		self._output_bucket_max_size = self.Config["output_bucket_max_size"]

		self._output_queue_max_size = int(self.Config['output_queue_max_size'])

		self._output_queue = asyncio.Queue(self._output_queue_max_size, loop=app.Loop)
		self._started = True

		self._output_bucket = ""

		app.PubSub.subscribe("Application.tick!", self._on_tick)
		app.PubSub.subscribe("Application.exit!", self._on_exit)


		self._future = asyncio.ensure_future(self._submit())


	def consume(self, data):
		self._output_bucket += data
		if len(self._output_bucket) > self._output_bucket_max_size:
			self.flush()
			assert self._output_queue.qsize() <= self._output_queue_max_size
			if self._output_queue.qsize() == self._output_queue_max_size:
				self.PubSub.publish("InfluxDBConnection.pause!", self)


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
				L.error("Influx error observed, returned: '{}' (should be None)".format(r))
			except:
				L.exception("Influx error observed, restoring the order")


			self._future = asyncio.ensure_future(self._submit())			

		self.flush()


	def flush(self, event_name=None):
		if len(self._output_bucket) == 0:
			return

		assert(self._output_bucket is not None)
		self._output_queue.put_nowait(self._output_bucket)
		#TODO: Handle queue full
		self._output_bucket = ""


	async def _submit(self):
		# A cycle that regularly sends buckets if there are any
		while self._started:
			_output_bucket = await self._output_queue.get()
			if _output_bucket is None:
				break
			if self._output_queue.qsize() == self._output_queue_max_size - 1:
				self.PubSub.publish("InfluxDBConnection.unpause!", self, asynchronously=True)			
			# Sending the data asynchronously
			async with aiohttp.ClientSession() as session:
				async with session.post(self.url, data=_output_bucket) as resp:
					print("resp: '{}'".format(resp))
					if resp.status != 204:
						resp_body = await resp.text()
						L.error("Failed to insert a line into Influx status:{} body:{}".format(resp.status, resp_body))
						raise RuntimeError("Failed to insert line into Influx")
					else:
						resp_body = await resp.text()
						print("resp_body: '{}'".format(resp_body))
						respj = json.loads(resp_body)
						if respj.get('errors', True) != False:
							#TODO: Iterate thru respj['items'] and display only status != 201 items in L.error()
							L.error("Failed to insert a line into Influx status:{} body:{}".format(resp.status, resp_body))
							raise RuntimeError("Failed to insert line into Influx")




