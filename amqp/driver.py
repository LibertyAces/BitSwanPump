import asyncio
import logging
import pika
import pika.adapters.asyncio_connection

from asab import Config
#

L = logging.getLogger(__name__)

#

class AMQPDriver(object):
	def __init__(self):
		self.connection = None
		self.reconnect_timeout = 10.0

		self.connected = asyncio.Event()
		self.connected.clear()

		self.channel = None

		self._on_connection_open_callbacks = set()
		self._on_connection_close_callbacks = set()
		self._on_channel_open_callbacks = set()

		self.reconnect();


	def reconnect(self):
		if self.connection is not None:
			if not (self.connection.is_closing or self.connection.is_closed):
				self.connection.close()
			self.connection = None

		self.channel = None

		parameters = pika.URLParameters(Config['amqp']['uri'])
		if parameters.client_properties is None:
			parameters.client_properties = dict()
		parameters.client_properties['application'] = Config['amqp']['appname']

		self.connection = pika.adapters.asyncio_connection.AsyncioConnection(
			parameters = parameters,
			on_open_callback=self._on_connection_open,
			on_open_error_callback=self._on_connection_open_error,
			on_close_callback=self._on_connection_close
		)


	# Connection callbacks

	def _on_connection_open(self, connection):
		L.info("AMQP connected")
		connection.channel(on_open_callback=self._on_channel_open)
		for callback in self._on_connection_open_callbacks:
			callback(connection)

	def on_connection_open(self, callback):
		self._on_connection_open_callbacks.add(callback)


	def _on_connection_close(self, connection, code, reason):
		L.warn("AMQP disconnected ({}): {}".format(code, reason))
		self.connection.add_timeout(self.reconnect_timeout, self.reconnect)
		self.channel = None

		for callback in self._on_connection_close_callbacks:
			callback(connection, code, reason)

	def on_connection_close(self, callback):
		self._on_connection_close_callbacks.add(callback)


	def _on_connection_open_error(self, connection, error_message=None):
		L.error("AMQP error: {}".format(error_message if error_message is not None else 'Generic error'))
		self.connection.add_timeout(self.reconnect_timeout, self.reconnect)
		self.channel = None


	# Channel callbacks

	def _on_channel_open(self, channel):
		L.info("AMQP channel open")
		self.channel = channel

		for callback in self._on_channel_open_callbacks:
			callback(channel)

	def on_channel_open(self, callback):
		self._on_channel_open_callbacks.add(callback)

###