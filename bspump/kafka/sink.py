import asyncio
import logging

import confluent_kafka

import asab

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

	Standard Kafka configuration options can be used,
	as specified in librdkafka library,
	where the options are simply passed to:

	https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
	"""

	ConfigDefaults = {
		"topic": "unconfigured",
		"watermark.low": "40000",
		"watermark.high": "90000",
		"batch.num.messages": "100000",
		"linger.ms": "500",  # This settings makes a significant impact on the throughtput
		"batch.size": "1000000",
		# "compression.type": "snappy",
	}


	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.ProducerConfig = {}
		self.Running = False
		self.PollTask = None

		connection = pipeline.locate_connection(app, connection)

		# Copy connection options
		for key, value in connection.Config.items():
			self.ProducerConfig[key.replace("_", ".")] = value

		# Copy configuration options, avoid the topic
		for key, value in self.Config.items():

			if key == "topic" or key.startswith("watermark"):
				continue

			self.ProducerConfig[key.replace("_", ".")] = value

		self.Producer = confluent_kafka.Producer(self.ProducerConfig, logger=L)

		self.Topic = self.Config["topic"]
		self.LowWatermark = int(self.Config["watermark.low"])
		self.HighWatermark = int(self.Config["watermark.high"])

		app.PubSub.subscribe_all(self)
		pipeline.PubSub.subscribe("bspump.pipeline.start!", self._on_start)
		pipeline.PubSub.subscribe("bspump.pipeline.stop!", self._on_stop)


	@asab.subscribe("Application.tick!")
	def _on_tick(self, event_name):

		if not self.Pipeline.is_ready():

			if len(self.Producer) < self.LowWatermark:
				self.Pipeline.throttle(self, False)


	def process(self, context, event: bytes):

		try:
			self.Producer.produce(
				context["kafka_topic"] if "kafka_topic" in context else self.Topic,
				value=event,
				key=context["kafka_key"] if "kafka_key" in context else None,
				headers=context["kafka_headers"] if "kafka_headers" in context else None,
			)

		except Exception as e:
			L.exception("Error occurred when sending data to Kafka: '{}'".format(e))

		if self.Pipeline.is_ready():

			if len(self.Producer) > self.HighWatermark:
				self.Pipeline.throttle(self, True)


	def _on_start(self, event_name, pipeline):

		if self.Pipeline != pipeline:
			return

		if self.Running:
			# Already started
			return

		assert(self.PollTask is None)
		self.Running = True
		proactor_svc = self.Pipeline.App.get_service('asab.ProactorService')
		self.PollTask = proactor_svc.execute(self._kafka_poll)


	async def _on_stop(self, event_name, pipeline):
		if self.PollTask is None:
			return

		# TODO: Wait till the ouput queue is trully empty

		poll_task = self.PollTask
		self.Running = False
		self.PollTask = None

		try:
			await poll_task
		except asyncio.CancelledError:
			pass


	def _kafka_poll(self):

		while self.Running:
			self.Producer.poll(500)
