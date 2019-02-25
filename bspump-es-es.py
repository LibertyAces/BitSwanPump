#!/usr/bin/env python3
import logging
import bspump
import bspump.elasticsearch
import bspump.file
import bspump.common
import bspump.trigger

###

L = logging.getLogger(__name__)

###


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		request_body = {
			"size": 20,
			"query": { 
				"bool" : {
					"must": [

						{
							"range" : {
								"@timestamp" : {
									"gt": "2019-02-24 23:59:59.999", #change date here
									"lt": "2019-02-25 23:59:59.999",
									"format": "yyyy-MM-dd HH:mm:ss.SSS",
								},
							},
						},
					]
				},		
			},
		}

		
		self.build(
			bspump.elasticsearch.ElasticSearchSource(
					app, 
					self, 
					"ESConnection1", 
					request_body=request_body,
					paging=False,
					config={'index': 'bs_xdr_a_*'} #change index here
					).on(bspump.trigger.PubSubTrigger(app, "go!", pubsub=self.PubSub)),
			bspump.elasticsearch.ElasticSearchSink(app, self, "ESConnection2")
			# bspump.common.PPrintSink(app, self)
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")
	svc.add_connection(
		bspump.elasticsearch.ElasticSearchConnection(app, "ESConnection1")
	)
	# svc.add_connection(
	# 	bspump.elasticsearch.ElasticSearchConnection(app, "ESConnection2")
	# )
	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	pl.PubSub.publish("go!")

	app.run()
