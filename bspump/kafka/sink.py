import asyncio
import json
import logging
import typing

from ..abc.sink import Sink

#

L = logging.getLogger(__name__)

#


class KafkaSink(Sink):
	"""
	KafkaSink is a sink processor that forwards the event to a Apache Kafka specified by a KafkaConnection object.

	KafkaSink expects bytes as an input. If the input is string or dictionary, it is automatically transformed to bytes
	using encoding charset specified in the configuration.

.. code:: python

	class KafkaPipeline(bspump.Pipeline):

		def __init__(self, app, pipeline_id):
			super().__init__(app, pipeline_id)
			self.build(
				bspump.kafka.KafkaSource(app, self, "KafkaConnection", config={'topic': 'messages'}),
				bspump.kafka.KafkaSink(app, self, "KafkaConnection", config={'topic': 'messages2'}),
		)

	There are two ways to use KafkaSink:
	- Specify a single topic in KafkaSink config - topic, to be used for all the events in pipeline.
	- Specify topic separetly for each event in event context - context['kafka_topic'].
		Topic from configuration is than used as a default topic.
		To provide business logic for event distribution, you can create topic selector processor.
	Processor example:

.. code:: python

	class KafkaTopicSelector(bspump.Processor):

		def process(self, context, event):
			if event.get("weight") > 10:
				context["kafka_topic"] = "heavy"
			else:
				context["kafka_topic"] = "light"

			return event

	Every kafka message can be a key:value pair. Key is read from event context - context['kafka_key'].
	If kafka_key is not provided, key defaults to None.
	"""

	ConfigDefaults = {
		"topic": "",
		"encoding": "utf-8",
		"output_queue_max_size": 100,

		"client_id": "",  # defaults set in AIOKafka
		"metadata_max_age_ms": "",
		"request_timeout_ms": "",
		"api_version": "",
		"acks": "",
		"key_serializer": "",
		"value_serializer": "",
		"max_batch_size": "",
		"max_request_size": "",
		"linger_ms": "",
		"send_backoff_ms": "",
		"retry_backoff_ms": "",
		"connections_max_idle_ms": "",
		"enable_idempotency": "",
		"transactional_id": "",
		"transaction_timeout_ms": "",
	}


	def __init__(self, app, pipeline, connection, key_serializer=None, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Connection = pipeline.locate_connection(app, connection)
		self.Topic = self.Config['topic']
		self._key_serializer = key_serializer
		self.Encoding = self.Config['encoding']

		self._output_queue = asyncio.Queue(loop=app.Loop)
		self._output_queue_max_size = int(self.Config['output_queue_max_size'])
		assert (self._output_queue_max_size >= 1)
		self._conn_future = None

		producer_param_definition = {
			"client_id": str,
			"metadata_max_age_ms": int,
			"request_timeout_ms": int,
			"api_version": str,
			"max_batch_size": int,
			"max_request_size": int,
			"linger_ms": int,
			"send_backoff_ms": int,
			"retry_backoff_ms": int,
			"connections_max_idle_ms": int,
			"enable_idempotence": bool,
			"transactional_id": str,
			"transaction_timeout_ms": int
		}
		self._producer_params = {
			x: producer_param_definition[x](y)
			for x, y in self.Config.items() if x in producer_param_definition.keys() and y != ""
		}

		if self.Config.get("acks") is not None:  # Mixed int with strings, needs special care
			if self.Config["acks"] in (0, 1, -1, "0", "1", "-1"):
				self._producer_params["acks"] = int(self.Config["acks"])
			if self.Config["acks"] == "all":
				self._producer_params["acks"] = self.Config["acks"]

		# Subscription
		self._on_health_check('connection.open!')
		app.PubSub.subscribe("Application.stop!", self._on_application_stop)
		app.PubSub.subscribe("Application.tick!", self._on_health_check)


	def _on_health_check(self, message_type):
		if self._conn_future is not None:
			# Connection future exists

			if not self._conn_future.done():
				# Connection future didn't result yet
				# No sanitization needed
				return

			try:
				self._conn_future.result()
			except Exception:
				# Connection future threw an error
				L.exception("Unexpected connection future error")

			# Connection future already resulted (with or without exception)
			self._conn_future = None

		assert (self._conn_future is None)

		self._conn_future = asyncio.ensure_future(
			self._connection(),
			loop=self.Loop
		)


	def _on_application_stop(self, message_type, counter):
		self._output_queue.put_nowait((None, None, None))


	async def _connection(self):
		producer = await self.Connection.create_producer(**self._producer_params)
		try:
			await producer.start()
			while True:
				topic, message, kafka_key = await self._output_queue.get()

				if topic is None and message is None:
					break

				if self._output_queue.qsize() == self._output_queue_max_size - 1:
					self.Pipeline.throttle(self, False)

				await producer.send_and_wait(topic, message, key=kafka_key)

		finally:
			await producer.stop()


	def process(self, context, event: typing.Union[dict, str, bytes]):
		if type(event) == dict:
			event = json.dumps(event)
			event = event.encode(self.Encoding)
		elif type(event) == str:
			event = event.encode(self.Encoding)
		kafka_topic = context.get("kafka_topic", self.Topic)
		kafka_key = context.get("kafka_key")


		if self._key_serializer is not None and kafka_key is not None:
			kafka_key = self._key_serializer(kafka_key)

		self._output_queue.put_nowait((kafka_topic, event, kafka_key))

		if self._output_queue.qsize() == self._output_queue_max_size:
			self.Pipeline.throttle(self, True)
