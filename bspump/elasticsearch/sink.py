import logging

from ..abc.sink import Sink
from .connection import ElasticSearchBulk

from .data_feeder import data_feeder_create_or_index

#

L = logging.getLogger(__name__)

#


class ElasticSearchSink(Sink):
	"""
	ElasticSearchSink allows you to insert events into ElasticSearch through POST requests

	The following attributes can be passed to the context and thus override the default behavior
	of the sink:

	es_index (STRING): ElasticSearch index name

	data_feeder accepts the event as its only parameter and yields data as Python generator
	The example implementation is:

	def data_feeder_create_or_index(event):
		_id = event.pop("_id", None)

		if _id is None:
			yield b'{"create":{}}\n'
		else:
			yield orjson.dumps(
				{"index": {"_id": _id}}, option=orjson.OPT_APPEND_NEWLINE
			)

		yield orjson.dumps(event, option=orjson.OPT_APPEND_NEWLINE)

	"""

	ConfigDefaults = {
		"index_prefix": "bspump_",  # Obsolete, use 'index'
		"index": "bspump_",
	}

	def __init__(self, app, pipeline, connection, id=None, config=None, bulk_class=ElasticSearchBulk, data_feeder=data_feeder_create_or_index):
		super().__init__(app, pipeline, id=id, config=config)

		self.Connection = pipeline.locate_connection(app, connection)
		self.BulkClass = bulk_class

		self.Index = self.Config.get('index')
		if self.Index is None or len(self.Index) == 0:
			L.warning("The 'index_prefix' has been renamed to 'index', adjust the configuration.")
			self.Index = self.Config.get('index_prefix')

		if data_feeder is None:
			raise RuntimeError("data_feeder must not be None.".format(data_feeder))

		self.DataFeeder = data_feeder

		app.PubSub.subscribe("ElasticSearchConnection.pause!", self._connection_throttle)
		app.PubSub.subscribe("ElasticSearchConnection.unpause!", self._connection_throttle)


	def process(self, context, event):
		self.Connection.consume(
			context.get("es_index", self.Index),
			self.DataFeeder(event),
			bulk_class=self.BulkClass,
		)

	def _connection_throttle(self, event_name, connection):
		if connection != self.Connection:
			return

		if event_name == "ElasticSearchConnection.pause!":
			self.Pipeline.throttle(self, True)
		elif event_name == "ElasticSearchConnection.unpause!":
			self.Pipeline.throttle(self, False)
		else:
			raise RuntimeError("Unexpected event name '{}'".format(event_name))
