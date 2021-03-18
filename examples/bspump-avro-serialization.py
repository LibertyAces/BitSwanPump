#!/usr/bin/env python3
import logging
import bspump.avro
import bspump
import bspump.common
import bspump.file
import bspump.trigger

###

L = logging.getLogger(__name__)

###



class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.file.FileCSVSource(app, self, config={
				'path': './data/sample-for-avro.csv',
				'delimiter': ';',
				'post': 'noop',
			}).on(bspump.trigger.PubSubTrigger(
				app, "go!", pubsub=self.PubSub
			)),
			bspump.avro.AvroSerializer(app, self, config={
				'schema_file': './data/sample-for-avro-schema.avsc',
			}),
			bspump.avro.AvroDeserializer(app, self, config={
				'schema_file': './data/sample-for-avro-schema.avsc',
			}),
			bspump.common.PPrintSink(app, self)
		)

		self.PubSub.subscribe("bspump.pipeline.cycle_end!", self.on_cycle_end)


	def on_cycle_end(self, event_name, pipeline):
		'''
		This ensures that at the end of the file scan, the target file is closed
		'''
		self.App.stop()


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	pl.PubSub.publish("go!")

	app.run()
