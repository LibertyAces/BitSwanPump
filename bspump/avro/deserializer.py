#!/usr/bin/env python3
import logging
import io
import bspump.avro.serializer
import fastavro
import bspump.trigger

###

L = logging.getLogger(__name__)

###

class AvroDeserializer(bspump.Generator):

	ConfigDefaults = {
		'schema': '',
		'schema_file': '',  # Used if 'schema is not present'
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Schema = bspump.avro.serializer.load_avro_schema(self.Config)


	async def generate(self, context, event, depth):
		fi = io.BytesIO(event)
		for record in fastavro.reader(fi, self.Schema):
			self.Pipeline.inject(context, record, depth)


###
