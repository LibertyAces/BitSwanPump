import asab
from baspump.abcproc import Source


class RabbitMQSource(bspump.Source):

	def __init__(self, app, pipeline, driver):
		super().__init__(app, pipeline)

		self.channel = None
		self.consumer_tag = None
		self.queue = asyncio.Queue(maxsize=1000, loop=app.Loop)

		self.prefetch = int(asab.Config['amqp']['prefetch'])

		driver.on_connection_open(self._on_connection_open)
		driver.on_connection_close(self._on_connection_close)
		driver.on_channel_open(self._on_channel_open)


	def _on_connection_open(self, connection):
		print("_on_connection_open")
		self.channel = connection.channel(on_open_callback=self._on_channel_open)
		self.consumer_tag = None

	def _on_connection_close(self, connection, code, reason):
		print("_on_connection_close")
		self.channel = None
		self.consumer_tag = None

	def _on_channel_open(self, channel):
		print("_on_channel_open")
		# Set Qoq
		channel.basic_qos(self._on_qos_applied, prefetch_count=self.prefetch);

	def _on_qos_applied(self, channel):
		print("_on_qos_applied")
		self.consumer_tag = self.channel.basic_consume(self._on_consume_message, asab.Config['amqp']['queue'])

	def _on_consume_message(self, channel, method, properties, body):
		print("_on_consume_message")
		self.queue.put_nowait({
			"channel": channel,
			"method": method,
			"properties": properties,
			"body": body
		})

	async def get(self):
		message = await self.queue.get()
		return message
