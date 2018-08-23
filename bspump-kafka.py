#!/usr/bin/env python3
import bspump
import bspump.common
import bspump.kafka
import bspump.trigger


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.kafka.KafkaSource(app, self, "KafkaConnection", config={'topic': 'messages'}),
			bspump.common.PPrintSink(app, self)
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_connection(
		bspump.kafka.KafkaConnection(app, "KafkaConnection")
	)

	svc.add_pipelines(
		SamplePipeline(app, "SamplePipeline"),
	)

	app.run()
