import asab
import asyncio
from ..abcproc import Source


class AMQPSource(Source):


	ConfigDefaults = {
		'queue': 'q',
		'error_exchange': 'error',
		'prefetch_count': '1000',
	}


	def __init__(self, app, pipeline, connection, id=None):
		super().__init__(app, pipeline, id)

		self._connection = pipeline.get_connection(app, connection)
		self._channel = None
		self._started = False
		self._consumer_tag = None
		self._error_exchange = self.Config['error_exchange']

		self._connection.PubSub.subscribe("AMQPConnection.open!", self._on_connection_open)


	async def start(self):
		await self._connection.ConnectionEvent.wait()
		self._channel = self._connection.Connection.channel(on_open_callback=self._on_channel_open)
		self._consumer_tag = None


	def _on_connection_open(self, event_name):
		if self._started:
			self._channel = self._connection.Connection.channel(on_open_callback=self._on_channel_open)
			self._consumer_tag = None

	def _on_channel_open(self, channel):
		# Set Qoq
		channel.basic_qos(self._on_qos_applied, prefetch_count=int(self.Config['prefetch_count']));

	def _on_qos_applied(self, channel):
		self._consumer_tag = self._channel.basic_consume(self._on_consume_message, self.Config['queue'])
		self._started = True

	def _on_consume_message(self, channel, method, properties, body):
		try:
			self.process(body)
		except:
			L.exception("Error when consuming message, message moved to error queue)")
			channel.basic_publish(
				self._error_exchange,
				method.exchange,
				body,
				properties=properties
			)
			channel.basic_nack(method.delivery_tag, requeue=False)

		else:
			channel.basic_ack(method.delivery_tag)
