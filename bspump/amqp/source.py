import asab
import asyncio
from ..abcproc import Source


class AMQPSource(Source):

	def __init__(self, app, pipeline, connection):
		super().__init__(app, pipeline)

		self._connection = pipeline.get_connection(app, connection)
		self._channel = None
		self._started = False
		self._consumer_tag = None

		self._conf_prefetch_count = int(asab.Config['amqp']['prefetch_count'])
		self._conf_error_exchange = asab.Config['amqp']['error_exchange']
		self._conf_queue = asab.Config['amqp']['queue']

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
		channel.basic_qos(self._on_qos_applied, prefetch_count=self._conf_prefetch_count);

	def _on_qos_applied(self, channel):
		self._consumer_tag = self._channel.basic_consume(self._on_consume_message, self._conf_queue)
		self._started = True

	def _on_consume_message(self, channel, method, properties, body):
		try:
			self.process(body)
		except:
			L.exception("Error when consuming message, message moved to error queue)")
			channel.basic_publish(
				self._conf_error_exchange,
				method.exchange,
				body,
				properties=properties
			)
			channel.basic_nack(method.delivery_tag, requeue=False)

		else:
			channel.basic_ack(method.delivery_tag)
