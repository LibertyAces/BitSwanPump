from bspump.appbuilder import ApplicationBuilder 
import logging


##
L = logging.getLogger(__name__)
##


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
	definition = "bspump/pipeline-builder-definition-test.json"
	app_builder = ApplicationBuilder(definition)
	app = app_builder.create_application()
	app = MyApplication()
	app.run()
