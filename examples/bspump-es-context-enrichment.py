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


class ElasticContextEnricher(bspump.Processor):
	"""
	Index, _id and version can be specified in the event's context.

	If they are not specified, ElasticSearch will create custom _id
	and version. Index will be in this case created by the specified rollover_mechanism.
	"""

	def process(self, context, event):

		context["es_index"] = "bs_example_es_sink"
		name = event.get("name")
		if name is not None:
			context["es_id"] = name.replace(" ", "").lower()
			context["es_version"] = 1

		return event


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.file.FileLineSource(app, self, config={
				'path': './data/es_sink.json',
				'post': 'noop',
			}).on(bspump.trigger.RunOnceTrigger(app)),
			bspump.common.JsonBytesToDictParser(app, self),
			ElasticContextEnricher(app, self),
			bspump.elasticsearch.ElasticSearchSink(app, self, "ESConnection")
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_connection(
		bspump.elasticsearch.ElasticSearchConnection(app, "ESConnection", config={
			"bulk_out_max_size": 100,
		}))

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()
