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


class RandomSource(bspump.TriggerSource):

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

	async def cycle(self):
		for i in range(0, 100_000):
			event = {
				'station': "Prague",
				'time': 123,
				'temp': 14,
			}
			await self.process(event)


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.sink = bspump.avro.AvroSink(app, self, config={
			'schema_file': './data/avro_schema.avsc',
			'file_name_template': './data/sink{index}.avro',
		})

		self.build(
			RandomSource(app, self).on(bspump.trigger.PubSubTrigger(
				app, "Application.run!", pubsub=self.App.PubSub
			)),
			self.sink
		)

		self.PubSub.subscribe("bspump.pipeline.cycle_end!", self.on_cycle_end)

	def on_cycle_end(self, event_name, pipeline):
		self.sink.rotate()
		self.App.stop()


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()
