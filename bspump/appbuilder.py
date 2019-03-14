import logging
import json
import importlib

from .abc import TriggerSource

##
L = logging.getLogger(__name__)
##


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
		connection_instance = connection_class.construct(app, connection)
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
		lookup_instance = lookup_class.construct(app, lookup)
		svc.add_lookup(lookup_instance)

	
	def create_pipelines(self, app):
		pipelines = self.Definition.get('pipelines')
		if pipelines is None:
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

		sources = self.create_processors(app, pipeline, sources_definition)
		pipeline.set_source(sources)
		processors = self.create_processors(app, pipeline, processors_definition)
		sink = self.create_processor(app, pipeline, sink_definition)

		processors.extend(sink)
		for processor in processors:
			pipeline.append_processor(processor)
		
		svc.add_pipeline(pipeline)


	def create_sources(self, app, pipeline, definition):
		
		sources = []
		for i in range(0, len(definition)):
			source_definition = definition[str(i)]
			source = self.create_processor(app, pipeline, source_definition)
			sources.append(source)

		return sources


	def create_source(self, app, pipeline, definition):
		module = importlib.import_module(definition["module"])
		processor_class = getattr(module, definition["class"])
		processor = processor_class.construct(app, pipeline, definition)
		if isinstance(processor, TriggerSource):
			trigger_definition = definition.get("trigger")
			if trigger_definition is None:
				return processor
			
			trigger = self.create_trigger(app, trigger_definition)
			return processor.on(trigger)
		
		return processor


	def create_trigger(self, app, definition):
		module = importlib.import_module(definition["module"])
		processor_class = getattr(module, definition["class"])
		trigger = construct(app, definition)
		return trigger

	
	def create_processors(self, app, pipeline, definition):
		if definition is None:
			return []
		
		processors = []
		for i in range(0, len(definition)):
			processor_definition = definition[str(i)]
			processor = self.create_processor(app, pipeline, processor_definition)
			processors.append(processor)

		return processors


	def create_processor(self, app, pipeline, definition):
		module = importlib.import_module(definition["module"])
		processor_class = getattr(module, definition["class"])
		processor = processor_class.construct(app, pipeline, definition)
		return processor