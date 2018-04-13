import datetime

import asab

from ..abc.sink import Sink

class MySQLSink(Sink):


	ConfigDefaults = {
		'query': ''
	}


	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self._connection = pipeline.locate_connection(app, connection)
		self._query = self.Config['query']

		app.PubSub.subscribe("MySQLConnection.pause!", self._connection_throttle)
		app.PubSub.subscribe("MySQLConnection.unpause!", self._connection_throttle)
		# self.Pipeline.throttle(self, True)


	def process(self, event):
		values = event

		# Prepare values for mysql query
		for col in values.keys():
			# NULL values
			if values[col] is None:
				values[col] = "NULL"
			# "Strings"
			elif isinstance(values[col], str):
				values[col] = "'{}'".format(values[col])
			elif isinstance(values[col], datetime.date):
				values[col] = "'"+str(values[col])+"'"

		self._connection.consume(
			self._query.format(**values))

	def _connection_throttle(self, event_name, connection):
		if connection != self._connection:
			return

		if event_name == "MySQLConnection.pause!":
			self.Pipeline.throttle(self, True)
		elif event_name == "MySQLConnection.unpause!":
			self.Pipeline.throttle(self, False)
		else:
			raise RuntimeError("Unexpected event name '{}'".format(event_name))

