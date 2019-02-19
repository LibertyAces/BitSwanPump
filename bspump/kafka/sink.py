import logging
import aiokafka

from ..abc.sink import Sink

#

L = logging.getLogger(__name__)

#


class KafkaSink(Sink):


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
