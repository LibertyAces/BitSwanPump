import logging
import aiokafka

from ..abc.sink import Sink

#

L = logging.getLogger(__name__)

#


class KafkaSink(Sink):
	"""
    KafkaSink is a sink processor that expects the event to be a user-defined message (such as string)
    and publishes it to a defined Apache Kafka instance configured in a KafkaConnection object.

.. code:: python

    class KafkaPipeline(bspump.Pipeline):

        def __init__(self, app, pipeline_id):
            super().__init__(app, pipeline_id)
            self.build(
                bspump.kafka.KafkaSource(app, self, "KafkaConnection", config={'topic': 'messages'}),
                bspump.kafka.KafkaSink(app, self, "KafkaConnection", config={'topic': 'messages2'}),
        )

    """

	ConfigDefaults = {
		'topic': '',
	}


	def __init__(self, app, pipeline, connection, key_serializer=None, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Connection = pipeline.locate_connection(app, connection)
		self.Topic = self.Config['topic']
		self._key_serializer = key_serializer

		app.PubSub.subscribe("KafkaConnection.pause!", self._connection_throttle)
		app.PubSub.subscribe("KafkaConnection.unpause!", self._connection_throttle)


	def process(self, context, event):
		self._consume_event(context, event, self.Topic)

	def _consume_event (self, context, event, topic):
		kafka_key = str.encode(context.get("kafka_key"))
		if self._key_serializer is not None:
			kafka_key = self._key_serializer(kafka_key)
		self.Connection.consume(topic, event, kafka_key)


	def _connection_throttle(self, event_name, connection):
		if connection != self.Connection:
			return

		if event_name == "KafkaConnection.pause!":
			self.Pipeline.throttle(self, True)
		elif event_name == "KafkaConnection.unpause!":
			self.Pipeline.throttle(self, False)
		else:
			raise RuntimeError("Unexpected event name '{}'".format(event_name))


class KafkaMultiSink (KafkaSink):
	"""
	KafkaMultiSink is an extension of the generic KafkaSink. It can feed multiple Kafka topics though.
	When you want to categorize pipeline events in to multiple kafka topics, provide the pipeline
	with some processor, that will set kafka_topic in event context and end it with KafkaMultiSink.
	'topic' in configuration is not being used by KafkaMultiSink.
	Processor example:
.. code:: python

	class KafkaTopicSelector(bspump.Processor):

		def process(self, context, event):
			if event.get("weight") > 10:
				context["kafka_topic"] = "heavy"
			else:
				context["kafka_topic"] = "light"

			return event
	"""

	def process(self, context, event):
		kafka_topic = context.get("kafka_topic")
		self._consume_event(context, event, kafka_topic)

