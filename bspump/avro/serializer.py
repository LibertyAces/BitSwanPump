#!/usr/bin/env python3
import logging
import io
import json
import fastavro
import bspump.trigger

###

L = logging.getLogger(__name__)

###


def load_avro_schema(config):
	schema = config.get('schema')
	if schema == '':
		schema_file = config.get('schema_file')
		if schema_file != '':
			with open(schema_file, 'r') as fi:
				schema = json.load(fi)

	if schema == '':
		raise RuntimeError("Avro scheme not read")

	return fastavro.parse_schema(schema)

class AvroSerializer(bspump.Generator):

	ConfigDefaults = {
		'schema': '',
		'schema_file': '',  # Used if 'schema is not present'
		'max_block_size': 10,
	}

	# TODO: Flush of the Records (in regular time interval and before the processor is finished)

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Schema = load_avro_schema(self.Config)

		self.MaxBlockSize = self.Config['max_block_size']
		self.Records = []


	async def generate(self, context, event, depth):
		self.Records.append(event)
		if len(self.Records) < self.MaxBlockSize:
			return None

		records = self.Records
		self.Records = []

		fo = io.BytesIO()
		fastavro.writer(fo, self.Schema, records)
		self.Pipeline.inject(context, fo.getbuffer(), depth)