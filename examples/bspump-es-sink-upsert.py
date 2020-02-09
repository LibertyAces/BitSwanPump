#!/usr/bin/env python3
import hashlib
import logging

import bspump
import bspump.common
import bspump.elasticsearch
import bspump.file
import bspump.trigger
from bspump import Processor

###

L = logging.getLogger(__name__)

###


class GenerateIdProcessor(Processor):

	def process(self, context, event):
		context["elasticsearch_operation_metadata"] = {
			"_id": hashlib.sha1(event.get("name").encode('utf-8')).hexdigest(),  # name will be unique in target index
			"_index": "override_custom_index"
		}

		context["elasticsearch_doc_metadata"] = {
			"doc_as_upsert": True
		}

		context["elasticsearch_operation"] = "update"

		return event


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.file.FileLineSource(app, self, config={
				'path': './data/es_sink_upsert.txt',
				'post': 'noop',
			}).on(bspump.trigger.RunOnceTrigger(app)),

			bspump.common.JsonBytesToDictParser(app, self),
			GenerateIdProcessor(app, self),
			bspump.elasticsearch.ElasticSearchSink(app, self, "ESConnection")
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_connection(
		bspump.elasticsearch.ElasticSearchConnection(app, "ESConnection", config={
			"bulk_out_max_size": 100
		}))

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()
