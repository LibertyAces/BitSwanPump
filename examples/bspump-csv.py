#!/usr/bin/env python3
import logging

import bspump
import bspump.common
import bspump.file
import bspump.trigger

###

L = logging.getLogger(__name__)

###


class SampleCSVPipeline(bspump.Pipeline):
	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.Source = bspump.file.FileCSVSource(
			app,
			self,
			config={
				"path": "./examples/data/countries.csv",
				"delimiter": ";",
				"post": "noop",  # one of 'delete', 'noop' and 'move'
			},
		)
		self.Sink = bspump.file.FileCSVSink(
			app, self, config={"path": "./examples/data/countries-out.csv"}
		)

		self.build(
			self.Source.on(bspump.trigger.RunOnceTrigger(app)),
			bspump.common.PPrintProcessor(app, self),
			self.Sink,
		)

		self.PubSub.subscribe("bspump.file_source.no_files!", self.on_no_files)
		self.PubSub.subscribe("bspump.pipeline.cycle_end!", self.on_cycle_end)

	def on_cycle_end(self, event_name, pipeline):
		"""
		This ensures that at the end of the file scan, the target file is closed.
		"""
		self.Sink.rotate()

	def on_no_files(self, event_name, pipeline):
		L.warning("No files found in the selected path.")


if __name__ == "__main__":
	app = bspump.BSPumpApplication()
	svc: bspump.BSPumpService = app.get_service("bspump.PumpService")

	# Construct and register Pipeline
	pipeline = SampleCSVPipeline(app, "SampleCSVPipeline")
	svc.add_pipeline(pipeline)

	app.run()
