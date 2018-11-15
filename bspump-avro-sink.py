#!/usr/bin/env python3
import logging
import asyncio
import asab
import bspump
import bspump.avro
import bspump.file
import bspump.common
import bspump.trigger

###

L = logging.getLogger(__name__)

###


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.sink = bspump.avro.AvroSink(app, self, 
			config={'path': './examples/data/avro_schema.avsc'})

		self.build(
			bspump.file.FileJSONSource(app, self, config={'path': './examples/data/sample.json'}).on(bspump.trigger.RunOnceTrigger(app)),
			self.sink
		)

		self.PubSub.subscribe("bspump.pipeline.cycle_end!", self.on_cycle_end)

	def on_cycle_end(self, event_name, pipeline):
		'''
		This ensures that at the end of the file scan, the target file is closed
		'''
		self.sink.rotate()


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()
