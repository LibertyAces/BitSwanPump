import asyncio
import logging
import pika
import pika.adapters.asyncio_connection

from asab import Config
from asab import PubSub
#

L = logging.getLogger(__name__)

#

class AMQPDriver(object):

	def __init__(self, app):
		self.Connection = None
		self.ConnectionEvent = asyncio.Event(loop=app.Loop)
		self.ConnectionEvent.clear()
		self._conf_reconnect_delay = float(Config['amqp']['reconnect_delay'])

		self.PubSub = PubSub(app)
		self.Loop = app.Loop

		self._reconnect();


	def _reconnect(self):
		if self.Connection is not None:
			if not (self.Connection.is_closing or self.Connection.is_closed):
				self.Connection.close()
			self.Connection = None

		parameters = pika.URLParameters(Config['amqp']['uri'])
		if parameters.client_properties is None:
			parameters.client_properties = dict()
		parameters.client_properties['application'] = Config['amqp']['appname']

		self.Connection = pika.adapters.asyncio_connection.AsyncioConnection(
			parameters = parameters,
			on_open_callback=self._on_connection_open,
			on_open_error_callback=self._on_connection_open_error,
			on_close_callback=self._on_connection_close
		)


	# Connection callbacks

	def _on_connection_open(self, connection):
		L.info("AMQP connected")
		self.ConnectionEvent.set()
		self.PubSub.publish("AMQPDriver.connection_open!")

	def _on_connection_close(self, connection, code, reason):
		L.warn("AMQP disconnected ({}): {}".format(code, reason))
		self.ConnectionEvent.clear()
		self.PubSub.publish("AMQPDriver.connection_close!")
		self.Loop.call_later(self._conf_reconnect_delay, self._reconnect)


	def _on_connection_open_error(self, connection, error_message=None):
		L.error("AMQP error: {}".format(error_message if error_message is not None else 'Generic error'))
		self.ConnectionEvent.clear()
		self.PubSub.publish("AMQPDriver.connection_open_error!")
		self.Loop.call_later(self._conf_reconnect_delay, self._reconnect)

