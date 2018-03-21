import logging
import asyncio
import aiohttp

import asab
import bspump

from .. import Sink

#

L = logging.getLogger(__name__)

#

class InfluxDBSink(Sink):

	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self._connection = pipeline.locate_connection(app, connection)

		app.PubSub.subscribe("InfluxDBConnection.pause!", self._connection_throttle)
		app.PubSub.subscribe("InfluxDBConnection.unpause!", self._connection_throttle)		


	def process(self, line):

		if isinstance(line, tuple):
			measurement, tag_set, field_set, timestamp = line
			wire_line = "{},{} {} {}\n".format(measurement, tag_set, field_set, int(timestamp * 1e9))

		elif isinstance(line, bytes):
			measurement = 'line'
			wire_line = line.decode('utf-8')
			if wire_line[-1:] != '\n': wire_line += '\n'

		# Passing the processed line to the connection
		self._connection.consume(wire_line)


	def flush(self):
		self._connection.flush()


	def _connection_throttle(self, event_name, connection):
		if connection != self._connection:
			return

		if event_name == "InfluxDBConnection.pause!":
			self.Pipeline.throttle(self, True)
		elif event_name == "InfluxdDBConnection.unpause!":
			self.Pipeline.throttle(self, False)
		else:
			raise RuntimeError("Unexpected event name '{}'".format(event_name))