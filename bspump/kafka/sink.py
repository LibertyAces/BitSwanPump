import json
import logging

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
		'encoding': 'utf-8',
	}


	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Connection = pipeline.locate_connection(app, connection)
		self.Topic = self.Config['topic']
		self.Encoding = self.Config['encoding']

		app.PubSub.subscribe("KafkaConnection.pause!", self._connection_throttle)
		app.PubSub.subscribe("KafkaConnection.unpause!", self._connection_throttle)


	def process(self, context, event):
		if type(event) == dict:
			event = json.dumps(event)
		if type(event) == str:
			event = event.encode(self.Encoding)
		self.Connection.consume(self.Topic, event)


	def _connection_throttle(self, event_name, connection):
		if connection != self.Connection:
			return

		if event_name == "KafkaConnection.pause!":
			self.Pipeline.throttle(self, True)
		elif event_name == "KafkaConnection.unpause!":
			self.Pipeline.throttle(self, False)
		else:
			raise RuntimeError("Unexpected event name '{}'".format(event_name))
