import logging

import orjson

from ..abc.sink import Sink
from .connection import ElasticSearchBulk

#

L = logging.getLogger(__name__)

#


class ElasticSearchSink(Sink):
	"""
	ElasticSearchSink allows you to insert events into ElasticSearch through POST requests

	The following attributes can be passed to the context and thus override the default behavior
	of the sink:

	es_index (STRING): ElasticSearch index name

	When specifying action: custom in the configuration,
	custom_data_feeder coroutine needs to be provided,
	which accepts items as its only parameter and yields data as Python generator.
	The example implementation is:

	async def my_data_feeder(items):
		for _id, data in items:
			yield b'{"create":{}}\n' if _id is None else orjson.dumps(
				{"index": {"_id": _id}}, option=orjson.OPT_APPEND_NEWLINE
			)
			yield data

	"""

	ConfigDefaults = {
		"index_prefix": "bspump_",  # Obsolete, use 'index'
		"index": "bspump_",
		'action': 'create',  # create, index, update, delete, custom
	}


	def __init__(self, app, pipeline, connection, id=None, config=None, bulk_class=ElasticSearchBulk, custom_data_feeder=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Connection = pipeline.locate_connection(app, connection)
		self.BulkClass = bulk_class

		self.Index = self.Config.get('index')

		# intex_prefix is obsolete. It is supported currently ensure backward compatibility
		if self.Index == "bspump_" and self.Config.get('index_prefix') != "bspump_" and len(self.Config.get('index_prefix')) > 0:
			L.warning("The 'index_prefix' has been renamed to 'index', please adjust the configuration.")
			self.Index = self.Config.get('index_prefix')

		# Data feeder selection based on action

		self.DataFeederMap = {
			"create": self._data_feeder_create,
			"index": self._data_feeder_index,
			"update": self._data_feeder_update,
			"delete": self._data_feeder_delete,
			"custom": custom_data_feeder,
		}

		action = self.Config["action"]
		self.DataFeeder = self.DataFeederMap.get(action)
		if self.DataFeeder is None:
			if action == "custom":
				raise RuntimeError("When specifying '{}' action, custom_data_feeder needs to be set.".format(action))
			else:
				raise RuntimeError("Action '{}' is not supported.".format(action))

		app.PubSub.subscribe("ElasticSearchConnection.pause!", self._connection_throttle)
		app.PubSub.subscribe("ElasticSearchConnection.unpause!", self._connection_throttle)


	def process(self, context, event):
		self.Connection.consume(
			context.get("es_index", self.Index),
			event.pop("_id", None),
			orjson.dumps(event, option=orjson.OPT_APPEND_NEWLINE),
			data_feeder=self.DataFeeder,
			bulk_class=self.BulkClass,
		)


	async def _data_feeder_create(self, items):
		for _id, data in items:
			yield b'{"create":{}}\n' if _id is None else orjson.dumps(
				{"index": {"_id": _id}}, option=orjson.OPT_APPEND_NEWLINE
			)
			yield data

	async def _data_feeder_index(self, items):
		for _id, data in items:
			yield b'{"index":{}}\n' if _id is None else orjson.dumps(
				{"index": {"_id": _id}}, option=orjson.OPT_APPEND_NEWLINE
			)
			yield data

	async def _data_feeder_update(self, items):
		for _id, data in items:
			yield b'{"update":{}}\n' if _id is None else orjson.dumps(
				{"index": {"_id": _id}}, option=orjson.OPT_APPEND_NEWLINE
			)
			yield data

	async def _data_feeder_delete(self, items):
		for _id, data in items:
			yield b'{"delete":{}}\n' if _id is None else orjson.dumps(
				{"index": {"_id": _id}}, option=orjson.OPT_APPEND_NEWLINE
			)
			yield data


	def _connection_throttle(self, event_name, connection):
		if connection != self.Connection:
			return

		if event_name == "ElasticSearchConnection.pause!":
			self.Pipeline.throttle(self, True)
		elif event_name == "ElasticSearchConnection.unpause!":
			self.Pipeline.throttle(self, False)
		else:
			raise RuntimeError("Unexpected event name '{}'".format(event_name))
