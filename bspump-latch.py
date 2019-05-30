#!/usr/bin/env python3
import bspump

from bspump.common import LatchProcessor


class LatchPipeline(bspump.Pipeline):
	def __init__(self, app, id=None):
		super().__init__(app, id)

		self.Source = bspump.common.InternalSource(app, self)

		self.build(
			self.Source,
			bspump.common.LatchProcessor(app, self, config={
				'queue_max_size': 25,
			}),
			bspump.common.PPrintSink(app, self)
		)

		app.PubSub.subscribe("Application.tick!", self.on_tick)
		app.PubSub.subscribe("Application.tick/10!", self.on_print)

	async def on_tick(self, message_type):
		if await self.ready():
			await self.Source.put_async({}, "Tick {}".format(message_type))

	async def on_print(self, message_type):
		latch = self.locate_processor("LatchProcessor")
		await self.Source.put_async({}, "Queue has {} items".format(len(latch.list_queue())))


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	# Construct and register Pipeline
	pl = LatchPipeline(app, "LatchPipeline")
	svc.add_pipeline(pl)

	app.run()
