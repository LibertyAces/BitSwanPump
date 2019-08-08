#!/usr/bin/env python3
import logging

import bspump
import bspump.avro
import bspump.common
import bspump.file
import bspump.trigger

###

L = logging.getLogger(__name__)

###


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.sink = bspump.avro.AvroSink(app, self, config={
			'schema_file': './data/avro_schema.avsc',
			'file_name_template': './data/sink{index}.avro',
		})

		self.build(
			bspump.file.FileJSONSource(app, self, config={
				'path': './data/sample_to_avro.json',
				'post': 'noop',
			}).on(bspump.trigger.RunOnceTrigger(app)),
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
