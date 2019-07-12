#!/usr/bin/env python3
import bspump
import bspump.common
import bspump.web
import bspump.http


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.WebSocketSource = bspump.http.WebSocketSource(app, self)

		self.build(
			self.WebSocketSource,
			bspump.common.PPrintSink(app, self)
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication(web_listen="0.0.0.0:8080")

	svc = app.get_service("bspump.PumpService")

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.WebContainer.WebApp.router.add_get('/bspump/ws', pl.WebSocketSource.handler)

	app.run()
