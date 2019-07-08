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
			bspump.file.FileCSVSource(
				app, self, config={'path': 'data/sample.csv', 'delimiter': ';', 'post': 'noop'}
			).on(bspump.trigger.RunOnceTrigger(app)),
			bspump.common.DictToJsonParser(app, self),
			bspump.common.JsonToDictParser(app, self),
			bspump.common.NullSink(app, self)
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	# Create and register all pipelines here

	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	pl.insert_before("DictToJsonParser", bspump.common.PPrintProcessor(app, pl))
	pl.insert_after("JsonToDictParser", bspump.common.PPrintProcessor(app, pl))

	app.run()
