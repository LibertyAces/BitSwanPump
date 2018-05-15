#!/usr/bin/env python3
import logging
import asyncio
import asab
import bspump
import bspump.file
import bspump.common
import bspump.trigger

###

L = logging.getLogger(__name__)

###

class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.file.FileCSVSource(app, self, config={'path': 'sample.csv'}).on(bspump.trigger.RunOnceTrigger(app)),
			bspump.common.PPrintSink(app, self)
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()
