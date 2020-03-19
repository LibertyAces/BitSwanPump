#!/usr/bin/env python3
import logging

import time

import bspump
import bspump.common
import bspump.random
import bspump.elasticsearch
import bspump.integrity
import bspump.file
import bspump.trigger

###

L = logging.getLogger(__name__)

###


"""

	This is an example of encrypting JSON data and enriching them by hash 
	which has been made by IntegrityEnricherProcessor. Those JSON data are
	then uploaded to ElasticSearch


	example of site.conf

	# ElasticSearch connection

	[connection:ESConnection]
	url=http://localhost:9200/

	# ElasticSearch sink

	[pipeline:SamplePipeline:ElasticSearchSink]
	index_prefix=bs_

"""


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		upper_bound = int(time.time())
		lower_bound = upper_bound - 100500
		self.build(
			bspump.file.FileLineSource(app, self, config={
				'path': './data/sampledata.json',
				'post': 'noop',
			}).on(bspump.trigger.RunOnceTrigger(app)),
			bspump.common.JsonBytesToDictParser(app, self),
			bspump.random.RandomEnricher(app, self, config={
				'field': '@timestamp',
				'lower_bound': lower_bound,
				'upper_bound': upper_bound
			}),
			bspump.integrity.IntegrityEnricherProcessor(app, self, 
				config={'key_path': './data/test_ec_key',
						'algorithm': 'HS512',
				}),
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
