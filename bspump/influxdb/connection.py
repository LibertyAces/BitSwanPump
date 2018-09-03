import logging
import asyncio
import aiohttp
import json

from asab import Config

from ..abc.connection import Connection


#

L = logging.getLogger(__name__)

#

class InfluxDBConnection(Connection):

	ConfigDefaults = {
		"url": 'http://localhost:8086/',
		'output_queue_max_size': 10,
		'output_bucket_max_size': 1000*1000,
		'timeout': 30,
		'db': 'mydb',
	}

	def __init__(self, app, connection_id, config=None):
		super().__init__(app, connection_id, config=config)

		self.url = self.Config["url"].strip()		
		if self.url[-1] != '/':
			self.url += '/'
		
		self._url_write = self.url + 'write?db=' + self.Config["db"]

		self._output_bucket_max_size = self.Config["output_bucket_max_size"]
		self._output_queue_max_size = int(self.Config['output_queue_max_size'])

		self._output_queue = asyncio.Queue(loop=app.Loop)
		self._started = True

		self._output_bucket = ""

		self.PubSub = app.PubSub
		self.PubSub.subscribe("Application.tick!", self._on_tick)
		self.PubSub.subscribe("Application.exit!", self._on_exit)

		self._future = asyncio.ensure_future(self._loader())


	def consume(self, data):
		self._output_bucket += data
		if len(self._output_bucket) > self._output_bucket_max_size:
			self.flush()


	async def _on_exit(self, event_name):
		self._started = False
		self.flush()
		await self._output_queue.put(None) # By sending None via queue, we signalize end of life
		await self._future # Wait till the _loader() terminates


	def _on_tick(self, event_name):
		if self._started and self._future.done():
			# Ups, _loader() task crashed during runtime, we need to restart it
			try:
				r = self._future.result()
				# This error should never happen
				L.error("Influx error observed, returned: '{}' (should be None)".format(r))
			except:
				L.exception("Influx error observed, restoring the order")


			self._future = asyncio.ensure_future(self._loader())			

		self.flush()


	def flush(self, event_name=None):
		if len(self._output_bucket) == 0:
			return

		assert(self._output_bucket is not None)
		self._output_queue.put_nowait(self._output_bucket)
		self._output_bucket = ""

		if self._output_queue.qsize() == self._output_queue_max_size:
			self.PubSub.publish("InfluxDBConnection.pause!", self)


	async def _loader(self):

		# A cycle that regularly sends buckets if there are any
		while self._started:
			_output_bucket = await self._output_queue.get()
			if _output_bucket is None:
				break

			if self._output_queue.qsize() == self._output_queue_max_size - 1:
				self.PubSub.publish("InfluxDBConnection.unpause!", self, asynchronously=True)			

			# Sending the data asynchronously
			async with aiohttp.ClientSession() as session:
				async with session.post(self._url_write, data=_output_bucket) as resp:
					resp_body = await resp.text()
					if resp.status != 204:
						L.error("Failed to insert a line into Influx status:{} body:{}".format(resp.status, resp_body))
						raise RuntimeError("Failed to insert line into Influx")
			
			# Should be empty
			if resp_body != '':
				L.warning("InfluxDB returned '{}', expected empty string".format(resp_body))

