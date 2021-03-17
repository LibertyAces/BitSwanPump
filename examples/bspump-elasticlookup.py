import logging

import bspump
import bspump.common
import bspump.elasticsearch
import bspump.file
import bspump.trigger

##

L = logging.getLogger(__name__)

##


class MyApplication(bspump.BSPumpApplication):
	def __init__(self):
		super().__init__()

		svc = self.get_service("bspump.PumpService")

		es_connection = bspump.elasticsearch.ElasticSearchConnection(self, "ElasticSearchConnection")
		svc.add_connection(es_connection)
		
		self.ElasticSearchLookup = bspump.elasticsearch.ElasticSearchLookup(
			self,
			connection=es_connection,
			id="ElasticSearchLookup",
			config={
				'key': 'user'
			})

		svc.add_lookup(self.ElasticSearchLookup)
		svc.add_pipeline(MyPipeline(self))
		

class MyPipeline(bspump.Pipeline):
	# Enriches the event with location from ES lookup
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.random.RandomSource(app, self,
				config={'number': 10, 'upper_bound': 10, 'field':'user', 'prefix':''}
			).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=1)),
			LocationEnricher(app, self),
			bspump.common.PPrintSink(app, self)
		)


class LocationEnricher(bspump.Generator):

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		svc = app.get_service("bspump.PumpService")
		self.Lookup = svc.locate_lookup("ElasticSearchLookup")


	async def generate(self, context, event, depth):
		if 'user' not in event:
			return None

		info = await self.Lookup.get(event['user'])

		# Inject a new event into a next depth of the pipeline
		await self.Pipeline.inject(context, event, depth)


	def process(self, context, event):
		if 'user' not in event:
			return None

		info = self.Lookup.get(event['user'])
		if info is not None:
			event['L'] = info.get('L')

		return event


if __name__ == '__main__':
	app = MyApplication()
	app.run()
