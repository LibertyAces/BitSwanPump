from bspump.mongodb import MongoDBLookup, MongoDBConnection

from bspump.file import FileCSVSource
from bspump.trigger import OpportunisticTrigger
from bspump.common import PPrintSink
from bspump import BSPumpApplication, Pipeline, Processor
import logging
import bspump.common

##
L = logging.getLogger(__name__)
##

class MyApplication(BSPumpApplication):
	def __init__(self):
		super().__init__()

		svc = self.get_service("bspump.PumpService")

		mongodb_connection = MongoDBConnection(self, "MongoDBConnection", config={
			"host":"mongodb://127.0.0.1:27017"})
		
		self.MongoDBLookup = MongoDBLookup(self, "MongoDBLookup", 
			mongodb_connection=mongodb_connection,
			config={
				'collection':'user_location',
				'database': 'users',
				'key': 'user'
			})

		svc.add_lookup(self.MongoDBLookup)
		svc.add_pipeline(MyPipeline(self))
		

class MyPipeline(Pipeline):
	# Enriches the event with location from Mogodb lookup
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		self.build(
			FileCSVSource(app, self, 
				config={"post":"noop", "path":"bspump/mongodb/var/users.csv"}
				).on(OpportunisticTrigger(app)),
			MyProcessor(app, self), 
			PPrintSink(app, self)
		)


class MyProcessor(Processor):

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		svc = app.get_service("bspump.PumpService")
		self.Lookup = svc.locate_lookup("MongoDBLookup")

	
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
