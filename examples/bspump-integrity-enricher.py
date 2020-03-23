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

	This is an example of encrypting JSON data from ElasticSearch and enriching them by hash 
	which has been made by IntegrityEnricher. JSON data are
	then uploaded to ElasticSearch.


	Example of site.conf

	# ElasticSearch connection

	[connection:ESConnection]
	url=http://localhost:9200/

	[connection:ESConnection2]
	url=http://localhost:9201/

	# ElasticSearch sink

	[pipeline:SamplePipeline:ElasticSearchSink]
	index_prefix=bs_

"""


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.elasticsearch.ElasticSearchSource(
				app, self, "ESConnection", config={
					"index": "bs_*"
				}
			).on(bspump.trigger.PubSubTrigger(app, "go!", pubsub=self.PubSub)),
			bspump.integrity.IntegrityEnricher(app, self, 
				config={'key_path': './data/test_ec_key',
						'algorithm': 'HS512',
				}),
			bspump.elasticsearch.ElasticSearchSink(app, self, "ESConnection2")
		)
		

if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_connection(
		bspump.elasticsearch.ElasticSearchConnection(app, "ESConnection", config={
			"bulk_out_max_size": 100,
		}))
	svc.add_connection(
		bspump.elasticsearch.ElasticSearchConnection(app, "ESConnection2"))

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	pl.PubSub.publish("go!")

	app.run()

