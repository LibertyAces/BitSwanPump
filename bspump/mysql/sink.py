import datetime

import asab

from ..abc.sink import Sink

class MySQLSink(Sink):


	ConfigDefaults = {
		'query': '',
		'rows_in_chunk': 1
	}


	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self._connection = pipeline.locate_connection(app, connection)
		self._query = self.Config['query']
		self.ChunkSize = self.Config['rows_in_chunk']

		if self.ChunkSize > 1:
			self.Chunk = []
		else:
			self.Chunk = False

		app.PubSub.subscribe("MySQLConnection.pause!", self._connection_throttle)
		app.PubSub.subscribe("MySQLConnection.unpause!", self._connection_throttle)
		# self.Pipeline.throttle(self, True)


	def process(self, context, event):
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

		if self.Chunk is False:
			self._connection.consume(
				self._query.format(**values))
		else:
			if len(self.Chunk) >= self.ChunkSize:
				self.flush()

			self.Chunk.append(tuple(values.values()))

	def flush(self):
		chunk = ''
		for row in self.Chunk:
			chunk += str(row) + ','

		chunk = chunk[:-1]

		self._connection.consume(
			self._query.format(chunk=chunk))

		self.Chunk = []

	def _connection_throttle(self, event_name, connection):
		if connection != self._connection:
			return

		if event_name == "MySQLConnection.pause!":
			self.Pipeline.throttle(self, True)
		elif event_name == "MySQLConnection.unpause!":
			self.Pipeline.throttle(self, False)
		else:
			raise RuntimeError("Unexpected event name '{}'".format(event_name))

	def rotate(self, new_filename=None):
		if self.Chunk is not False and len(self.Chunk) != 0:
			self.flush()
