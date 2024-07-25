#!/usr/bin/env python3
import logging
import io
import fastavro
from ..avro import loader
from ..abc.generator import Generator



###

L = logging.getLogger(__name__)

###


class AvroDeserializer(Generator):
	ConfigDefaults = {
		'schema_file': '',
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Schema = loader.load_avro_schema(self.Config)


	async def generate(self, context, event, depth):
		fi = io.BytesIO(event)

		if self.Schema is None:
			L.warning("Schema file is not provided.")
		else:
			L.warning("Schema file is used.")

		for record in fastavro.reader(fi, self.Schema):
			self.Pipeline.inject(context, record, depth)
