#!/usr/bin/env python3
import bspump
import bspump.common
import bspump.http

class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.Counter = 1

		self.Source = bspump.common.InternalSource(app, self)

		self.build(
			self.Source,
			bspump.http.HTTPClientWebSocketSink(app, self,
				config={
					'url': 'https://localhost:8081/logman/ws',
				}
			)
		)

		app.PubSub.subscribe("Application.tick!", self.on_tick)


	async def on_tick(self, message_type):
		if self.is_ready():
			await self.Source.put_async({}, "Tick {}!".format(self.Counter))
			self.Counter += 1


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()
