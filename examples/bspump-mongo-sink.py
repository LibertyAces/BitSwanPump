#!/usr/bin/env python3
import bspump
import bspump.common
import bspump.mongodb
import bspump.http

class MongoDBPipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.http.HTTPClientSource(app, self, config={
				'url': "http://ip.jsontest.com/"
			}).on(bspump.trigger.PeriodicTrigger(app, 5)),
			bspump.common.StdJsonToDictParser(app, self),
			bspump.common.PPrintProcessor(app, self),
			# MongoDB sink can accept dict or list of dicts
			bspump.mongodb.MongoDBSink(app, self, "MongoDBConnection", config={'collection': 'specific_collection'}),
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_connection(
		bspump.mongodb.MongoDBConnection(app, "MongoDBConnection")
	)

	svc.add_pipeline(
		MongoDBPipeline(app, "MongoDBPipeline")
	)

	app.run()
