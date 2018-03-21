#TODO: Obsoleted file, remove after Mar 2018

import asab
import logging
import bspump
import asyncio
import aiohttp

#


L = logging.getLogger(__name__)

#

class InfluxDBDriver(object):

	def __init__(self, app):
		self.url = asab.Config["influx"]["url"].strip()
		if self.url[-1] != '/':
			self.url += '/'
		self.url += 'write?db=' + asab.Config["influx"]["db"]

		self.output_bucket_max_size = 1000
		self.output_bucket = ""
		self.output_queue = asyncio.Queue(maxsize=1000, loop=app.Loop)

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
		#TODO: Handle queue full
		self.output_bucket = ""


	async def _submit(self, future):
		# A cycle that regularly sends buckets if there are any
		while True:
			output_bucket = await self.output_queue.get()
			# Sending the data asynchronously
			async with aiohttp.ClientSession() as session:
				print(output_bucket)
				async with session.post(self.url, data=output_bucket) as resp:
					if resp.status != 204:
						L.error("Failed to insert a line into InfluxDB: {}".format(resp.status))
		# Finishing the future
		future.set_result("done")


class InfluxDBSink(bspump.Sink):

	def __init__(self, app, pipeline, driver):
		super().__init__(app, pipeline)
		self._driver = driver

	def process(self, event):
		# Getting information from the data
		# Working with only one line
		wire_line = "{},{} {} {}\n".format(
			event['measurement'], event['tag_set'], event['field_set'], int(event['timestamp']))
		# Passing the processed line to the driver
		self._driver.consume(wire_line)

