import asyncio
import logging
import pika
import pika.adapters.asyncio_connection

from asab import Config
from asab import PubSub

from ..abcproc import Connection

#

L = logging.getLogger(__name__)

#

class AMQPConnection(Connection):

	def __init__(self, app):
		super().__init__(app)

		self.Connection = None
		self.ConnectionEvent = asyncio.Event(loop=app.Loop)
		self.ConnectionEvent.clear()

		self.PubSub = PubSub(app)
		self.Loop = app.Loop

		self._conf_reconnect_delay = float(Config['amqp']['reconnect_delay'])
		self._conf_url = Config['amqp']['url']
		self._conf_appname = Config['amqp']['appname']

		self._reconnect();


	def _reconnect(self):
		if self.Connection is not None:
			if not (self.Connection.is_closing or self.Connection.is_closed):
				self.Connection.close()
			self.Connection = None

		parameters = pika.URLParameters(self._conf_url)
		if parameters.client_properties is None:
			parameters.client_properties = dict()
		parameters.client_properties['application'] = self._conf_appname

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
		self.PubSub.publish("AMQPConnection.open!")

	def _on_connection_close(self, connection, code, reason):
		L.warn("AMQP disconnected ({}): {}".format(code, reason))
		self.ConnectionEvent.clear()
		self.PubSub.publish("AMQPConnection.close!")
		self.Loop.call_later(self._conf_reconnect_delay, self._reconnect)


	def _on_connection_open_error(self, connection, error_message=None):
		L.error("AMQP error: {}".format(error_message if error_message is not None else 'Generic error'))
		self.ConnectionEvent.clear()
		self.PubSub.publish("AMQPConnection.open_error!")
		self.Loop.call_later(self._conf_reconnect_delay, self._reconnect)

