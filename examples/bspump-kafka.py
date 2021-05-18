#!/usr/bin/env python3
import bspump
import bspump.common
import bspump.kafka


class KafkaPipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.kafka.KafkaSource(app, self, "KafkaConnection", config={'topic': 'messages'}),
			bspump.common.BytesToStringParser(app, self),
			bspump.common.StdJsonToDictParser(app, self),
			bspump.common.PPrintProcessor(app, self),
			# KafkaSink can accept both bytes,  str or dict
			bspump.kafka.KafkaSink(app, self, "KafkaConnection", config={'topic': 'messages2'}),
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_connection(
		bspump.kafka.KafkaConnection(app, "KafkaConnection")
	)

	svc.add_pipeline(
		KafkaPipeline(app, "KafkaPipeline")
	)

	app.run()
