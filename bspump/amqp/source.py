import asyncio
import logging

import pika
import pkg_resources

from ..abc.source import Source


L = logging.getLogger(__name__)


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

		self._connection.PubSub.subscribe("AMQPConnection.open!", self._on_connection_open)
		self._connection.PubSub.subscribe("AMQPConnection.close!", self._on_connection_close)


	async def main(self):

		if self._connection.ConnectionEvent.is_set() and self._channel is None:
			self._on_connection_open(".local!")

		try:
			while 1:
				await self._channel_ready.wait()
				await self.Pipeline.ready()
				method, properties, body = await self._queue.get()
				await self.process_message(method, properties, body)
				self._channel.basic_ack(method.delivery_tag)

		except asyncio.CancelledError:
			pass

		except BaseException as e:
			L.exception("Error when processing AMQP message")
			self.Pipeline.set_error(None, None, e)


		# Requeue rest of the messages
		while not self._queue.empty():
			method, properties, body = await self._queue.get()
			self._channel.basic_nack(method.delivery_tag, requeue=True)

		if self._channel is not None:
			self._channel.close()
			self._channel = None
			self._channel_ready.clear()

	async def process_message(self, method, properties, body):
		context = {
			'amqp:method': method,
			'amqp:properties': properties
		}
		await self.process(body, context=context)


	def _on_connection_open(self, event_name):
		assert self._channel is None
		self._channel = self._connection.Connection.channel(on_open_callback=self._on_channel_open)
		self._channel_ready.set()


	def _on_connection_close(self, event_name):
		self._channel = None
		self._channel_ready.clear()

	def _on_qos_applied(self, channel):
		if pkg_resources.parse_version(pika.__version__) >= pkg_resources.parse_version('1.0.a'):
			self._channel.basic_consume(self.Config['queue'], self._on_consume_message)
		else:
			self._channel.basic_consume(self._on_consume_message, self.Config['queue'])

	def _on_channel_open(self, channel):
		channel.basic_qos(callback=self._on_qos_applied, prefetch_count=int(self.Config['prefetch_count']))


	def _on_consume_message(self, channel, method, properties, body):
		try:
			self._queue.put_nowait((method, properties, body))
		except Exception:
			channel.basic_nack(method.delivery_tag, requeue=True)

	@classmethod
	def construct(cls, app, pipeline, definition: dict):
		newid = definition.get('id')
		config = definition.get('config')
		connection = definition['args']['connection']
		return cls(app, pipeline, connection, newid, config)


class AMQPFullMessageSource(AMQPSource):

	def process_message(self, method, properties, body):
		self.process((method, properties, body))
