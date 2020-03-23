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

	This is an example of encrypting JSON data from ElasticSearh and enriching them by hash 
	which has been made by IntegrityEnricher. Then the data integrity is checked by 
	IntegrityChecker.


	Example of site.conf

	# ElasticSearch connection
	[connection:ESConnection]
	url=http://127.0.0.1:9200

	[connection:ESConnectionLocal]
	url=http://127.0.0.1:9201

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
			bspump.elasticsearch.ElasticSearchSource(
				app, self, "ESConnection", config={
					"index": "bs_xdr_sbr_ilm-000002" # TODO: change it to bs_* 
				}
			).on(bspump.trigger.PubSubTrigger(app, "go!", pubsub=self.PubSub)),
			bspump.integrity.IntegrityEnricher(app, self, 
				config={'key_path': './data/test_ec_key',
						'algorithm': 'HS512',
				}),
			bspump.elasticsearch.ElasticSearchSink(app, self, "ESConnectionLocal")
		)


class SamplePipeline2(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.elasticsearch.ElasticSearchSource(
				app, self, "ESConnectionLocal", config={
					"index": "bs_xdr_sbr_ilm-000002" # TODO: change it to bs_* 
				}
			).on(bspump.trigger.PeriodicTrigger(app, 1)),
			bspump.integrity.IntegrityChecker(app, self, "ESConnectionLocal",
				config={'key_path': './data/test_ec_key',
						'algorithm': 'HS512',
						'index': 'bs_xdr_sbr_ilm-000002', # TODO: change it to bs_
						'items_size': 20
				}),
			bspump.common.NullSink(app, self)
		)
		

if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_connection(
		bspump.elasticsearch.ElasticSearchConnection(app, "ESConnection", config={
			"bulk_out_max_size": 100,
		}))
	svc.add_connection(
		bspump.elasticsearch.ElasticSearchConnection(app, "ESConnectionLocal"))

	pl = SamplePipeline(app, 'SamplePipeline')
	pl2 = SamplePipeline2(app, 'SamplePipeline2')
	svc.add_pipeline(pl)
	svc.add_pipeline(pl2)

	pl.PubSub.publish("go!")

	app.run()
