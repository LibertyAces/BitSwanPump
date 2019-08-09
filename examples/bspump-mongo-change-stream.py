from bspump import BSPumpApplication, Pipeline
import bspump.trigger
import bspump.common
import bspump.mongodb
import logging



##
L = logging.getLogger(__name__)
##


class MyApplication(BSPumpApplication):
	def __init__(self):
		super().__init__()
		svc = self.get_service("bspump.PumpService")
		svc.add_connection(bspump.mongodb.MongoDBConnection(self, config={
			"host":"mongodb://127.0.0.1:27017"}))
		svc.add_pipeline(MyPipeline0(self))
		

class MyPipeline0(Pipeline):
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.mongodb.MongoDBChangeStreamSource(app, self, "MongoDBConnection", config={'database':'users', 
				'collection':'user_location'}),
			bspump.common.PPrintSink(app, self)
		)


if __name__ == '__main__':
	app = MyApplication()
	app.run()
