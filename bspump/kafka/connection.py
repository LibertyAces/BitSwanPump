import asyncio
import aiokafka
import logging

from ..abc.connection import Connection

#

L = logging.getLogger(__name__)

#


class KafkaConnection(Connection):

	ConfigDefaults = {
		'bootstrap_servers': 'localhost:9092',
		'output_queue_max_size': 100,
		'disabled': 0
	}


	def __init__(self, app, connection_id, config=None):
		super().__init__(app, connection_id, config=config)

		self.Loop = app.Loop

		self._output_queue = asyncio.Queue(loop=app.Loop)
		self._output_queue_max_size = int(self.Config['output_queue_max_size'])
		self._conn_future = None

		# Subscription
		self.PubSub = app.PubSub

		if int(self.Config['disabled']) == 0:
			self._on_health_check('connection.open!')
			self.PubSub.subscribe("Application.stop!", self._on_application_stop)
			self.PubSub.subscribe("Application.tick!", self._on_health_check)


	def _on_health_check(self, message_type):
		if self._conn_future is not None:
			# Connection future exists

			if not self._conn_future.done():
				# Connection future didn't result yet
				# No sanitization needed
				return

			try:
				self._conn_future.result()
			except:
				# Connection future threw an error
				L.exception("Unexpected connection future error")
				
			# Connection future already resulted (with or without exception)
			self._conn_future = None

		assert(self._conn_future is None)

		self._conn_future = asyncio.ensure_future(
			self._connection(),
			loop=self.Loop
		)


	def _on_application_stop(self, message_type, counter):
		self._output_queue.put_nowait((None, None))


	async def _connection(self):
		producer = aiokafka.AIOKafkaProducer(
			loop=self.Loop,
			bootstrap_servers=self.get_bootstrap_servers()
		)
		try:
			await producer.start()
			await self._loader(producer=producer)
		except BaseException as e:
			L.exception("Unexpected Kafka Error.")
		finally:
			await producer.stop()

	def get_bootstrap_servers(self):
		return self.Config['bootstrap_servers'].split(';')


	def consume(self, topic, message):
		self._output_queue.put_nowait((topic, message))
		if self._output_queue.qsize() == self._output_queue_max_size:
			self.PubSub.publish("KafkaConnection.pause!", self)


	async def _loader(self, producer):
		while True:
			topic, message = await self._output_queue.get()

			if topic is None and message is None:
				break

			if self._output_queue.qsize() == self._output_queue_max_size - 1:
				self.PubSub.publish("KafkaConnection.unpause!", self, asynchronously=True)

			await producer.send_and_wait(topic, message)
