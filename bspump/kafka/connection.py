import asyncio

import aiokafka
import logging

from ..abc.connection import Connection

#

L = logging.getLogger(__name__)

#


class KafkaConnection(Connection):
	"""
	KafkaConnection serves to connect BSPump application with an instance of Apache Kafka messaging system.
	It can later be used by processors to consume or provide user-defined messages.

.. code:: python

	config = {"compression_type": "gzip"}
	app = bspump.BSPumpApplication()
	svc = app.get_service("bspump.PumpService")
	svc.add_connection(
		bspump.kafka.KafkaConnection(app, "KafkaConnection", config)
	)

..


	``ConfigDefaults`` options:

		* ``compression_type``: Kafka supports several compression types: ``gzip``, ``snappy`` and ``lz4``.
		  This option needs to be specified in Kafka Producer only, Consumer will decompress automatically.

	"""

	ConfigDefaults = {
		'bootstrap_servers': 'localhost:9092',
		'compression_type': '',
		'disabled': 0,
		'output_queue_max_size': 100,
	}


	def __init__(self, app, id=None, config=None):
		super().__init__(app, id=id, config=config)

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
		self._output_queue.put_nowait((None, None, None))


	async def _connection(self):
		producer = aiokafka.AIOKafkaProducer(
			loop=self.Loop,
			bootstrap_servers=self.get_bootstrap_servers(),
			compression_type=self.get_compression(),
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


	def get_compression(self):
		"""
		Returns compression type to use in connection
		"""
		compression_type = self.Config.get("compression_type")
		if compression_type in ("", "none", "None"):
			compression_type = None
		return compression_type


	def consume(self, topic, message, kafka_key=None):
		"""
		Consumes a user-defined message by storing it in a queue and later publishing to Apache Kafka.
		"""
		self._output_queue.put_nowait((topic, message, kafka_key))
		if self._output_queue.qsize() == self._output_queue_max_size:
			self.PubSub.publish("KafkaConnection.pause!", self)


	async def _loader(self, producer):
		while True:
			topic, message, kafka_key = await self._output_queue.get()

			if topic is None and message is None:
				break

			if self._output_queue.qsize() == self._output_queue_max_size - 1:
				self.PubSub.publish("KafkaConnection.unpause!", self, asynchronously=True)

			await producer.send_and_wait(topic, message, key=kafka_key)
