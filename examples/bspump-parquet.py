#!/usr/bin/env python3
import logging

import bspump
import bspump.common
import bspump.file
import bspump.parquet
import bspump.trigger

###

L = logging.getLogger(__name__)

###


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.Sink = bspump.parquet.ParquetSink(app, self, config={
			'rows_in_chunk': 500,
			'rows_per_file': 1000,
			'schema_file': './data/sample2-schema.json',
			'file_name_template': './data/ignore_sink{index}.parquet',
		})

		self.build(
			bspump.file.FileCSVSource(app, self, config={
				'path': './data/sample2.csv',
				'delimiter': ',',
				'post': 'noop',
			}).on(bspump.trigger.RunOnceTrigger(app)),
			self.Sink
		)

		self.PubSub.subscribe("bspump.pipeline.cycle_end!", self.on_cycle_end)

	def on_cycle_end(self, event_name, pipeline):
		"""
		This ensures that at the end of the file scan, the target file is closed
		"""
		self.Sink.rotate()


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()
