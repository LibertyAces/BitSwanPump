#!/usr/bin/env python3
import bspump
import bspump.common
import bspump.subprocess


class EmptyFilterProcessor(bspump.Processor):
	def process(self, context, event):
		if event:
			return event


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.subprocess.SubProcessSource(app, self, config={
				'command': 'tail -n 2 data/es_sink.json',
				'ok_return_codes': '0,1'
			}),
			EmptyFilterProcessor(app, self),
			bspump.common.JsonToDictParser(app, self),
			bspump.common.PPrintSink(app, self)
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_pipeline(SamplePipeline(app, "SamplePipeline"))

	app.run()
