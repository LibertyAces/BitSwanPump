import orjson

"""
Data feeders to be used in ElasticSearchSink.
"""


def data_feeder_create_or_index(event):
	_id = event.pop("_id", None)

	if _id is None:
		yield b'{"create":{}}\n'
	else:
		yield orjson.dumps(
			{"index": {"_id": _id}}, option=orjson.OPT_APPEND_NEWLINE
		)

	yield orjson.dumps(event, option=orjson.OPT_APPEND_NEWLINE)


def data_feeder_create(event):
	_id = event.pop("_id", None)

	if _id is None:
		yield b'{"create":{}}\n'
	else:
		yield orjson.dumps(
			{"create": {"_id": _id}}, option=orjson.OPT_APPEND_NEWLINE
		)

	yield orjson.dumps(event, option=orjson.OPT_APPEND_NEWLINE)


def data_feeder_index(event):
	_id = event.pop("_id", None)

	if _id is None:
		yield b'{"index":{}}\n'
	else:
		yield orjson.dumps(
			{"index": {"_id": _id}}, option=orjson.OPT_APPEND_NEWLINE
		)

	yield orjson.dumps(event, option=orjson.OPT_APPEND_NEWLINE)


def data_feeder_update(event):
	_id = event.pop("_id", None)

	assert _id is not None, "_id must be present in the event when updating a document in ElasticSearch"

	yield orjson.dumps(
		{"update": {"_id": _id}}, option=orjson.OPT_APPEND_NEWLINE
	)

	yield orjson.dumps({"doc": event}, option=orjson.OPT_APPEND_NEWLINE)


def data_feeder_delete(event):
	_id = event.pop("_id", None)

	assert _id is not None, "_id must be present in the event when deleting a document from ElasticSearch"

	yield orjson.dumps(
		{"delete": {"_id": _id}}, option=orjson.OPT_APPEND_NEWLINE
	)

	assert len(event) == 0,\
		"When deleting items from ElasticSearch, no data should be provide, but '{}' found.".format(event)
