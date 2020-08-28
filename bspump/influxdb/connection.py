import asyncio
import logging
import re
import aiohttp

from ..abc.connection import Connection

#

L = logging.getLogger(__name__)


#


class InfluxDBConnection(Connection):
	"""
	InfluxDBConnection serves to connect BSPump application with an InfluxDB database.
	The InfluxDB server is accessed via URL, and the database is specified
	using the `db` parameter in the configuration.

.. code:: python

	app = bspump.BSPumpApplication()
	svc = app.get_service("bspump.PumpService")
	svc.add_connection(
		bspump.influxdb.InfluxDBConnection(app, "InfluxConnection1")
	)

	"""

	ConfigDefaults = {
		"url": 'http://localhost:8086/',
		'db': 'mydb',
		'output_queue_max_size': 10,
		'output_bucket_max_size': 1000 * 1000,
		'timeout': 30,
		'retry_enabled': False,
		'response_codes_to_retry': '404,502,503,504'
	}

	def __init__(self, app, id=None, config=None):
		super().__init__(app, id=id, config=config)

		self.url = self.Config["url"].strip()
		if self.url[-1] != '/':
			self.url += '/'

		self._url_write = self.url + 'write?db=' + self.Config["db"]

		self._output_bucket_max_size = int(self.Config["output_bucket_max_size"])
		self._output_queue_max_size = int(self.Config['output_queue_max_size'])
		self._timeout = aiohttp.ClientTimeout(total=int(self.Config['timeout']))
		self.RetryEnabled = self.Config.getboolean("retry_enabled")

		self.AllowedBulkResponseCodes = frozenset(
			[int(x) for x in re.findall(r"[0-9]+", self.Config['response_codes_to_retry'])]
		)

		self._output_queue = asyncio.Queue(loop=app.Loop)
		self._started = True

		self._output_bucket = ""

		self.PubSub = app.PubSub
		self.PubSub.subscribe("Application.tick!", self._on_tick)
		self.PubSub.subscribe("Application.exit!", self._on_exit)

		self._future = asyncio.ensure_future(self._loader())

	def consume(self, data):
		"""
		Consumes user-defined data to be stored in the InfluxDB database.
		"""
		self._output_bucket += data
		if len(self._output_bucket) > self._output_bucket_max_size:
			self.flush()

	async def _on_exit(self, event_name):
		self._started = False
		self.flush()
		await self._output_queue.put(None)  # By sending None via queue, we signalize end of life
		await self._future  # Wait till the _loader() terminates

	async def _on_tick(self, event_name):
		if self._started and self._future.done():
			# Ups, _loader() task crashed during runtime, we need to restart it
			try:
				r = self._future.result()
				# This error should never happen
				L.error("Influx error observed, returned: '{}' (should be None)".format(r))
			except Exception as e:
				L.exception(f"Influx error, {e}, observed, restoring the order")

			self._future = asyncio.ensure_future(self._loader())
		self.flush()

	def flush(self, event_name=None):
		"""
		Directly flushes the content of the internal bucket with data to InfluxDB database.
		"""
		if len(self._output_bucket) == 0:
			return

		assert (self._output_bucket is not None)
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

			try:
				async with aiohttp.ClientSession(timeout=self._timeout) as session:
					async with session.post(self._url_write, data=_output_bucket) as resp:
						resp_body = await resp.text()
						if resp.status in self.AllowedBulkResponseCodes and self.RetryEnabled:
							L.warning(
								f"Retryable response code recieved, retrying. Queue size {self._output_queue.qsize()}"
							)
							self._output_queue.put_nowait(_output_bucket)
							self.PubSub.publish("InfluxDBConnection.pause!", self)
							await asyncio.sleep(3)
							self.PubSub.publish("InfluxDBConnection.unpause!", self)

						elif resp.status is None:
							L.error(
								"Failed to insert a line into Influx status:{} body:{}".format(resp.status, resp_body))
							raise RuntimeError("Failed to insert line into Influx")

			# Here we define errors, that we want to retry
			except OSError:
				if self.RetryEnabled:
					L.warning(f"Retryable exception raised, retrying. Queue size {self._output_queue.qsize()}")
					self._output_queue.put_nowait(_output_bucket)
					self.PubSub.publish("InfluxDBConnection.pause!", self)
					await asyncio.sleep(3)
					self.PubSub.publish("InfluxDBConnection.unpause!", self)
