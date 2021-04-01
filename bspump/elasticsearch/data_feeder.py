import orjson

"""
Data feeders to be used in ElasticSearchSink.
"""


async def data_feeder_create_or_index(items):
	for _id, data in items:
		yield b'{"create":{}}\n' if _id is None else orjson.dumps(
			{"index": {"_id": _id}}, option=orjson.OPT_APPEND_NEWLINE
		)
		yield data


async def data_feeder_create(items):
	for _id, data in items:
		yield b'{"create":{}}\n' if _id is None else orjson.dumps(
			{"create": {"_id": _id}}, option=orjson.OPT_APPEND_NEWLINE
		)
		yield data


async def data_feeder_index(items):
	for _id, data in items:
		yield b'{"index":{}}\n' if _id is None else orjson.dumps(
			{"index": {"_id": _id}}, option=orjson.OPT_APPEND_NEWLINE
		)
		yield data


async def data_feeder_update(items):
	for _id, data in items:
		yield orjson.dumps(
			{"update": {"_id": _id}}, option=orjson.OPT_APPEND_NEWLINE
		)
		update_data = b'{"doc":' + data[:-1] + b'}\n'
		yield update_data


async def data_feeder_delete(items):
	for _id, data in items:
		yield orjson.dumps(
			{"delete": {"_id": _id}}, option=orjson.OPT_APPEND_NEWLINE
		)
		assert data is None or data == b'{}\n',\
			"When deleting items from ElasticSearch, no data should be provide, but '{}' found.".format(data)
