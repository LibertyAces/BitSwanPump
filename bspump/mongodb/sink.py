import logging

from ..abc.sink import Sink

from .connection import data_feeder_update, MongoDBBulk

#

L = logging.getLogger(__name__)

#


class MongoDBSink(Sink):

	"""
	MongoDBSink is a sink processor that forwards the event to a MongoDB specified
	by a MongoDBConnection object.

	MongoDBSink expects either a dictionary or a list of dictionaries as an input.

	Example code can be found in the examples section under bspump-mongo-sink.py

	While the connection defines MongoDB database used, you need to specify particular collection
	inside of this database in the sink itself by modifying the ConfigDefaults while instantiating
	the class.

	"""

	ConfigDefaults = {
		"collection": "collection",  # Default collection
	}

	def __init__(self, app, pipeline, connection, id=None, config=None, bulk_class=MongoDBBulk, data_feeder=data_feeder_update):
		"""
		Description:

		**Parameters**

		app : Application
				Name of the Application

		pipeline : Pipeline
				Name of the Pipeline

		connection : Connection
				Name of the Connection

		id : ID, default= None
				ID

		config : JSON, default= None
				Configuration file with additional information.

		bulk_class=MongoDBBulk :

		data_feeder=data_feeder_update :
		"""
		super().__init__(app, pipeline, id=id, config=config)

		self.Connection = pipeline.locate_connection(app, connection)
		self.BulkClass = bulk_class
		self.CollectionName = self.Config["collection"]

		if data_feeder is None:
			raise RuntimeError("data_feeder must not be None.")

		self.__data_feeder = data_feeder

		app.PubSub.subscribe("MongoDBConnection.pause!", self._connection_throttle)
		app.PubSub.subscribe("MongoDBConnection.unpause!", self._connection_throttle)


	def process(self, context, event):
		"""
		Description:

		**Parameters**

		context :

		event : any data type
				Information with timestamp.
		"""

		try:
			_id = event.pop("_id", None)

		except TypeError:

			if isinstance(event, dict) is False:
				L.error("You are trying to pass event of type: {} to MongoDBConnection, but only dict is supported".format(type(event)))
			raise

		self.Connection.consume(
			context.get("collection", self.CollectionName),
			self.__data_feeder(event, _id),
			bulk_class=self.BulkClass,
		)


	def _connection_throttle(self, event_name, connection):

		if connection != self.Connection:
			return

		if event_name == "MongoDBConnection.pause!":
			self.Pipeline.throttle(self, True)

		elif event_name == "MongoDBConnection.unpause!":
			self.Pipeline.throttle(self, False)

		else:
			raise RuntimeError("Unexpected event name '{}'".format(event_name))
