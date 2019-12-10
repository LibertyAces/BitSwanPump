from ..abc.sink import Sink


class PostgreSQLSink(Sink):


	ConfigDefaults = {
		'query': '',
		'data': '',
	}


	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self._connection = pipeline.locate_connection(app, connection)
		self._query = self.Config['query']
		self._data_keys = self.Config['data'].split(',')

		app.PubSub.subscribe("PostgreSQLConnection.pause!", self._connection_throttle)
		app.PubSub.subscribe("PostgreSQLConnection.unpause!", self._connection_throttle)


	def process(self, context, event):
		# Prepare data
		data = tuple(event.get(x) for x in self._data_keys)

		# Consume
		self._connection.consume(self._query, data)


	def _connection_throttle(self, event_name, connection):
		if connection != self._connection:
			return

		if event_name == "PostgreSQLConnection.pause!":
			self.Pipeline.throttle(self, True)
		elif event_name == "PostgreSQLConnection.unpause!":
			self.Pipeline.throttle(self, False)
		else:
			raise RuntimeError("Unexpected event name '{}'".format(event_name))
