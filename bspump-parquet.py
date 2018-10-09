#!/usr/bin/env python3
import logging
import asyncio
import asab
import bspump
import bspump.parquet
import bspump.file
import bspump.common
import bspump.trigger

###

L = logging.getLogger(__name__)

###

class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.sink = bspump.parquet.ParquetSink(app, self, config={'path': 'output.parquet', 'chunk_size': 500})

		self.build(
			bspump.file.FileCSVSource(app, self, config={'path': 'sample.csv', 'delimiter': ';'}).on(bspump.trigger.RunOnceTrigger(app)),
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
