#!/usr/bin/env python3
import bspump
import bspump.common
import bspump.kafka


class KafkaPipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.kafka.KafkaSource(app, self, "KafkaConnection", config={
				'topic': 'messages1',
				'group_id': 'test',
			}),
			bspump.common.BytesToStringParser(app, self),
			bspump.common.StdJsonToDictParser(app, self),
			bspump.common.PPrintProcessor(app, self),
			bspump.common.StdDictToJsonParser(app, self),
			bspump.common.StringToBytesParser(app, self),
			bspump.kafka.KafkaSink(app, self, "KafkaConnection", config={
				'topic': 'messages2'
			}),
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_connection(
		bspump.kafka.KafkaConnection(app, "KafkaConnection", config={
			"bootstrap_servers": "localhost:9092",
		})
	)

	svc.add_pipeline(
		KafkaPipeline(app, "KafkaPipeline")
	)

	app.run()
