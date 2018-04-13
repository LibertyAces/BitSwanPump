import asab
import asyncio

from ..abc.source import Source


class AMQPSource(Source):


	ConfigDefaults = {
		'queue': 'q',
		'error_exchange': 'error',
		'prefetch_count': '1000',
	}


	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self._connection = pipeline.locate_connection(app, connection)
		self._channel = None
		self._channel_ready = asyncio.Event(loop=app.Loop)
		self._channel_ready.clear()
		self._error_exchange = self.Config['error_exchange']
		self._queue = asyncio.Queue(loop=app.Loop)



	async def main(self):
		self._connection.PubSub.subscribe("AMQPConnection.open!", self._on_connection_open)
		self._connection.PubSub.subscribe("AMQPConnection.close!", self._on_connection_close)

		if self._connection.ConnectionEvent.is_set() and self._channel is None:
			self._channel = self._connection.Connection.channel(on_open_callback=self._on_channel_open)
			self._channel_ready.set()

		try:
			while 1:
				await self._channel_ready.wait()
				await self.Pipeline.ready()
				method, properties, body = await self._queue.get()
				self.process_message(method, properties, body)
				self._channel.basic_ack(method.delivery_tag)

		except asyncio.CancelledError:
			pass

		# Requeue rest of the messages
		while not self._queue.empty():
			method, properties, body = await self._queue.get()
			self._channel.basic_nack(method.delivery_tag, requeue=True)

		if self._channel is not None:
			self._channel.close()
			self._channel = None
			self._channel_ready.clear()


	def process_message(self, method, properties, body):
		context = {
			'ampq:method': method,
			'ampq:properties': properties
		}
		self.process(body, context=context)


	def _on_connection_open(self, event_name):
		assert self._channel is None
		self._channel = self._connection.Connection.channel(on_open_callback=self._on_channel_open)
		self._channel_ready.set()


	def _on_connection_close(self, event_name):
		self._channel = None
		self._channel_ready.clear()


	def _on_channel_open(self, channel):
		channel.basic_qos(self._on_qos_applied, prefetch_count=int(self.Config['prefetch_count']));


	def _on_qos_applied(self, channel):
		self._channel.basic_consume(self._on_consume_message, self.Config['queue'])


	def _on_consume_message(self, channel, method, properties, body):
		try:
			self._queue.put_nowait((method, properties, body))
		except:
			channel.basic_nack(method.delivery_tag, requeue=True)

class AMQPFullMessageSource(AMQPSource):

	def process_message(self, method, properties, body):
		self.process((method, properties, body))
