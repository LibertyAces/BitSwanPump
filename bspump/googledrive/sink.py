from ..abc.sink import Sink


class GoogleDriveSink(Sink):

	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Connection = pipeline.locate_connection(app, connection)

		app.PubSub.subscribe("GoogleDriveConnection.pause!", self._connection_throttle)
		app.PubSub.subscribe("GoogleDriveConnection.unpause!", self._connection_throttle)

	def _connection_throttle(self, event_name, connection):
		if connection != self.Connection:
			return

		if event_name == "GoogleDriveConnection.pause!":
			self.Pipeline.throttle(self, True)
		elif event_name == "GoogleDriveConnection.unpause!":
			self.Pipeline.throttle(self, False)
		else:
			raise RuntimeError("Unexpected event name '{}'".format(event_name))

	def process(self, context, event):
		self.Connection.consume(event, context)
