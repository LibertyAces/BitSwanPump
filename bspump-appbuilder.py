from bspump.appbuilder import ApplicationBuilder 
from bspump.abc.processor import Processor
import logging


##
L = logging.getLogger(__name__)
##


class Processor00(Processor):
	def process(self, context, event):
		# print(event, "quak!!!!!!!")
		return event


class Processor10(Processor):

	def __init__(self, app, pipeline, lookup, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		svc = app.get_service("bspump.PumpService")
		self.Lookup = svc.locate_lookup(lookup)
	
	def process(self, context, event):

		return event


	@classmethod
	def construct(cls, app, pipeline, definition:dict):
		newid = definition.get('id')
		config = definition.get('config')
		lookup = definition['args']['lookup']
		return cls(app, pipeline, lookup, newid, config)


class Processor11(Processor):	
	def process(self, context, event):

		return event


if __name__ == '__main__':
	definition = "bspump/pipeline-builder-definition-test1.json"
	app_builder = ApplicationBuilder(definition)
	app = app_builder.create_application()
	# print(app)
	app.run()
