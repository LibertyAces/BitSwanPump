import logging

import bspump
import bspump.common
import bspump.random
import bspump.mongodb
import bspump.trigger

##

L = logging.getLogger(__name__)


##


class MyApplication(bspump.BSPumpApplication):
	def __init__(self):
		super().__init__()

		svc = self.get_service("bspump.PumpService")

		mongodb_connection = bspump.mongodb.MongoDBConnection(self, "MongoDBConnection", config={
			"host": "mongodb://10.17.173.29:27017",
		})

		self.MongoDBLookup = bspump.mongodb.MongoDBLookup(self, mongodb_connection, "MongoDBLookup", config={
			'collection': 'test_collection',
			'database': 'test_database',
			'key': 'author',
		})

		svc.add_lookup(self.MongoDBLookup)
		svc.add_pipeline(MyPipeline(self))


class MyPipeline(bspump.Pipeline):
	# Enriches the event with location from Mogodb lookup
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		self.build(

			bspump.random.RandomSource(app, self,
				config={'author':'author', 'prefix':'', 'upper_bound':10, 'number':1}
				).on(bspump.trigger.OpportunisticTrigger(app)),

			MyEnricher(app, self),
			bspump.common.PPrintSink(app, self),
			# bspump.common.NullSink(app, self),

		)


class MyEnricher(bspump.Generator):

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		svc = app.get_service("bspump.PumpService")
		self.Lookup = svc.locate_lookup("MongoDBLookup")


	async def generate(self, context, event, depth):
		# print("77777777777", int(event['user']))
		event = await self.Lookup.get("jouda")
		print(event)
		self.Pipeline.inject(context, event, depth)


if __name__ == '__main__':
	app = MyApplication()
	app.run()
