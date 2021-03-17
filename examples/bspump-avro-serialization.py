#!/usr/bin/env python3
import logging
import json
import io

import fastavro

import bspump
import bspump.avro
import bspump.common
import bspump.file
import bspump.trigger

###

L = logging.getLogger(__name__)

###


# Move this into a dedicate module and use it in Source, Sink, Serialized, Deserializer
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

		self.MaxBlockSize = 10  # TODO: Read this from config
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


class AvroDeserializer(bspump.Generator):

	ConfigDefaults = {
		'schema': '',
		'schema_file': '',  # Used if 'schema is not present'
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Schema = load_avro_schema(self.Config)


	async def generate(self, context, event, depth):
		fi = io.BytesIO(event)
		for record in fastavro.reader(fi, self.Schema):
			self.Pipeline.inject(context, record, depth)


###


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.file.FileCSVSource(app, self, config={
				'path': './data/sample-for-avro.csv',
				'delimiter': ';',
				'post': 'noop',
			}).on(bspump.trigger.PubSubTrigger(
				app, "go!", pubsub=self.PubSub
			)),
			AvroSerializer(app, self, config={
				'schema_file': './data/sample-for-avro-schema.avsc',
			}),
			AvroDeserializer(app, self, config={
				'schema_file': './data/sample-for-avro-schema.avsc',
			}),
			bspump.common.PPrintSink(app, self)
		)

		self.PubSub.subscribe("bspump.pipeline.cycle_end!", self.on_cycle_end)


	def on_cycle_end(self, event_name, pipeline):
		'''
		This ensures that at the end of the file scan, the target file is closed
		'''
		self.App.stop()


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	pl.PubSub.publish("go!")

	app.run()
