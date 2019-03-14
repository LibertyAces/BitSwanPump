import json
import importlib

class ApplicationBuilder(object):
	
	def __init__(self, definition):
		self.Definition = json.load(definition)
		print("definition:", self.Definition)

	def create_application(self, web_listen=None):
		app = BSPumpApplication(web_listen=web_listen)
		
		self.create_connections(app)
		self.create_lookups(app)
		self.create_pipelines(app)

		return app


	def create_connections(self, app):
		
		connections = self.Definition.get('connections')
		if connections is None:
			return 

		for i in range(0, len(connections)):
			connection_definition = connections[str(i)]
			self.create_connection(app, connection_definition)

	
	def create_connection(self, app, connection):
		svc = app.get_service("bspump.PumpService")
		module = importlib.import_module(connection["module"])
		connection_class = getattr(module, connection["class"])
		connection_instance = connection_class.construct(connection)
		svc.add_connection(connection_instance)


	def create_lookups(self, app):
		lookups = self.Definition.get('lookups')
		if lookups is None:
			return 

		for i in range(0, len(lookups)):
			lookup_definition = lookups[str(i)]
			self.create_lookup(app, lookup_definition)


	def create_lookup(self, app, lookup):
		svc = app.get_service("bspump.PumpService")
		module = importlib.import_module(lookup["module"])
		lookup_class = getattr(module, lookup["class"])
		lookup_instance = lookup_class.construct(lookup)
		svc.add_lookup(lookup_instance)

	
	def create_pipelines(self, app):
		pipelines = self.Definition.get('pipelines')
		pipelines is None:
			return 

		for i in range(0, len(pipelines)):
			pipeline_definition = pipelines[str(i)]
			self.create_pipeline(app, pipeline_definition)
		

	def create_pipeline(self, app, pipeline_definition):
		svc = app.get_service("bspump.PumpService")
		pipeline_id = pipeline_definition["id"]
		pipeline = bspump.Pipeline(app, pipeline_id)
		
		sources_definition = pipeline_definition["sources"]
		processors_definition = pipeline_definition.get("processors")
		sink = pipeline_definition["sink"]

		sources = self.create_processors(app, sources_definition)
		pipeline.set_source(sources)
		processors = self.create_processors(app, processors_definition)
		sink = self.create_processors(app, sink_definition)

		processors.extend(sink)
		for processor in processors:
			pipeline.append_processor(processor)
		
		svc.add_pipeline(pipeline)



	def create_processors(self, app, definition):
		if definition is None:
			return []
		
		processors = []
		for i in range(0, len(definition)):
			processor_definition = definition[str(i)]
			processor = self.create_processor(app, processor_definition)
			processors.append(processor)

		return processors


	def create_processor(self, app, definition):
		module = importlib.import_module(definition["module"])
		processor_class = getattr(module, definition["class"])
		processor = processor_class.construct(definition)
		return processor