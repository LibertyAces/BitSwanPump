#!/usr/bin/env python3
import logging
import io
import fastavro
from ..avro import loader
from ..abc.generator import Generator

L = logging.getLogger(__name__)

###


class AvroSerializer(Generator):

	ConfigDefaults = {
		'schema_file': '',
		'max_block_size': 10,
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Schema = loader.load_avro_schema(self.Config)
		self.MaxBlockSize = self.Config['max_block_size']
		self.Records = []

	# TODO: call this method also on_tick() to ensure proactive flushing of accumulated events

	async def generate(self, context, event, depth):
		self.Records.append(event)
		if len(self.Records) < self.MaxBlockSize:
			return None

		records = self.Records
		self.Records = []

		fo = io.BytesIO()

		if self.Schema is None:
			L.warning("Schema file is not provided , using schema from the AVRO")
		else:
			L.warning("Schema file is used.")

		fastavro.writer(fo, self.Schema, records)
		self.Pipeline.inject(context, fo.getbuffer(), depth)

