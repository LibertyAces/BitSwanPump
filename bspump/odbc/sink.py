from ..abc.sink import Sink


class ODBCSink(Sink):


	ConfigDefaults = {
		'query': '',  # e.g.: 'INSERT INTO table_name (first_name, last_name) VALUES (?, ?);'
		'data': '',  # e.g.: 'first_name,last_name'
	}


	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self._connection = pipeline.locate_connection(app, connection)
		self._query = self.Config['query']
		self._data_keys = self.Config['data'].split(',')

		app.PubSub.subscribe("ODBConnection.pause!", self._connection_throttle)
		app.PubSub.subscribe("ODBConnection.unpause!", self._connection_throttle)


	def process(self, context, event):
		# Prepare data
		data = tuple(event.get(x) for x in self._data_keys)

		# Consume
		self._connection.consume(self._query, data)


	def _connection_throttle(self, event_name, connection):
		if connection != self._connection:
			return

		if event_name == "ODBConnection.pause!":
			self.Pipeline.throttle(self, True)
		elif event_name == "ODBCConnection.unpause!":
			self.Pipeline.throttle(self, False)
		else:
			raise RuntimeError("Unexpected event name '{}'".format(event_name))
