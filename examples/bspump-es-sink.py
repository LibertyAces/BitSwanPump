#!/usr/bin/env python3
import logging

import bspump
import bspump.common
import bspump.elasticsearch
import bspump.file
import bspump.trigger

###

L = logging.getLogger(__name__)

###


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.file.FileLineSource(app, self, config={
				'path': './data/es_sink.json',
				'post': 'noop',
			}).on(bspump.trigger.RunOnceTrigger(app)),
			bspump.common.JsonBytesToDictParser(app, self),
			bspump.elasticsearch.ElasticSearchSink(app, self, "ESConnection")
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_connection(
		bspump.elasticsearch.ElasticSearchConnection(app, "ESConnection", config={
			"bulk_out_max_size": 100,
			# 'url': 'http://es01:9200;http://es02:9200;http://es03:9200;http://es04:9200',
		}))

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()
