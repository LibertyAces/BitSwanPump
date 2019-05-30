import logging

from ..abc.sink import Sink

#

L = logging.getLogger(__name__)

#


class KafkaSink(Sink):
	"""
    KafkaSink is a sink processor that forwards the event to a Apache Kafka specified by a KafkaConnection object.
    
    TODO: How to specify topic ...

    TODO: Key in context['kafka_key'] or None ...


.. code:: python

    class KafkaPipeline(bspump.Pipeline):

        def __init__(self, app, pipeline_id):
            super().__init__(app, pipeline_id)
            self.build(
                bspump.kafka.KafkaSource(app, self, "KafkaConnection", config={'topic': 'messages'}),
                bspump.kafka.KafkaSink(app, self, "KafkaConnection", config={'topic': 'messages2'}),
        )

    If you want to send all events to same topic, simply provide it in KafkaSink configuration in topic attribute.
    In case you want to distribute events to different topics on individual basis,
    you can use event context - context['kafka_topic'].
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
		kafka_topic = context.get("kafka_topic", self.Topic)
		kafka_key = context.get("kafka_key")

		# TODO: Make KafkaConnection create separate producer for every sink
		#  	- key/value serialization could be moved there.
		if self._key_serializer is not None:
			kafka_key = self._key_serializer(kafka_key)
		self.Connection.consume(kafka_topic, event, kafka_key)


	def _connection_throttle(self, event_name, connection):
		if connection != self.Connection:
			return

		if event_name == "KafkaConnection.pause!":
			self.Pipeline.throttle(self, True)
		elif event_name == "KafkaConnection.unpause!":
			self.Pipeline.throttle(self, False)
		else:
			raise RuntimeError("Unexpected event name '{}'".format(event_name))




