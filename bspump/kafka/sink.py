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


	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Connection = pipeline.locate_connection(app, connection)
		self.Topic = self.Config['topic']

		app.PubSub.subscribe("KafkaConnection.pause!", self._connection_throttle)
		app.PubSub.subscribe("KafkaConnection.unpause!", self._connection_throttle)


	def process(self, context, event):
		kafka_key_bytes = str.encode(context.get ("kafka_key"))
		self.Connection.consume(self.Topic, event, kafka_key_bytes)


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
	def process(self, context, event):
		topic = context.get("kafka_topic")
		kafka_key_bytes = str.encode(context.get("kafka_key"))
		self.Connection.consume(topic, event, kafka_key_bytes)