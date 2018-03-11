import pika
import asab
from .. import Sink

class AMQPSink(Sink):


	ConfigDefaults = {
		'exchange': 'amq.direct',
		'content_type': 'text/plain',
	}


	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self._connection = pipeline.get_connection(app, connection)
		self._channel = None
		self._exchange = self.Config['exchange']
		self._content_type = self.Config['content_type']


		app.PubSub.subscribe_all(self)

		self._connection.PubSub.subscribe("AMQPConnection.open!", self._on_connection_open)
		self._connection.PubSub.subscribe("AMQPConnection.close!", self._on_connection_close)
		if self._connection.ConnectionEvent.is_set():
			self._on_connection_open("simulated")


	@asab.subscribe("Application.tick/10!")
	def _on_tick(self, event_name):
		# Heal the connection
		if self._channel is None and self._connection.ConnectionEvent.is_set():
			self._on_connection_open("simulated")


	def _on_connection_open(self, event_name):
		self._connection.Connection.channel(on_open_callback=self._on_channel_open)

	def _on_connection_close(self, event_name):
		self._channel = None
		print("Close!")

	def _on_channel_open(self, channel):
		self._channel = channel
		print("Open!")


	def process(self, event):
		if self._channel is None:
			raise RuntimeError("AMQP channel is not open")

		try:
			self._channel.basic_publish(
				self._exchange,
				'test_routing_key',
				event,
				pika.BasicProperties(content_type=self._content_type, delivery_mode=1)
			)
		except pika.exceptions.ChannelClosed:
			self._channel = None
