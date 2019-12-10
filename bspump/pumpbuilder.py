import logging
import json
import importlib

from .pipeline import Pipeline

##
L = logging.getLogger(__name__)
##


class PumpBuilder(object):
	'''
	PumpBuilder is meant to create the pipeline with connections, processors, sources alternatively.
	``definition`` is a path to the json file, containing description of the pump.
	Example of such file:

.. code-block:: json

	{
		"pipelines" : [
			{
				"id": "MyPipeline0",
				"args": {},
				"config": {},
				"sources": [
					{
						"id": "FileCSVSource",
						"module": "bspump.file",
						"class" : "FileCSVSource",
						"args": {},
						"config": {"path":"etc/test.csv", "post":"noop"},
						"trigger": {
							"module": "bspump.trigger",
							"class": "OpportunisticTrigger",
							"id": "",
							"args": {}
						}
					}
				],
				"processors": [
					{
						"module":"bspump-pumpbuilder",
						"class": "Processor00",
						"args": {},
						"config": {}
					}
				],
				"sink": {
					"module":"bspump.common",
					"class": "PPrintSink",
					"args": {},
					"config": {}
				}
			}
		]
	}

	'''

	def __init__(self, definition):
		with open(definition) as f:
			self.Definition = json.load(f)


	def construct_pump(self, app, svc):
		'''
		The main method to construct the pump.
		``app`` is a BspumpApplication object, ``svc``` is service.
		Example of use:

	.. code-block:: python

		app = BSPumpApplication()
		svc = app.get_service("bspump.PumpService")
		pump_builder = PumpBuilder(definition)
		pump_builder.construct_pump(app, svc)
		app.run()

		'''
		self.construct_connections(app, svc)
		self.construct_lookups(app, svc)
		self.construct_pipelines(app, svc)


	def construct_connections(self, app, svc):

		connections = self.Definition.get('connections')
		if connections is None:
			return

		for i in range(0, len(connections)):
			connection_definition = connections[i]
			self.construct_connection(app, svc, connection_definition)


	def construct_connection(self, app, svc, connection):

		module = importlib.import_module(connection["module"])
		connection_class = getattr(module, connection["class"])
		connection_instance = connection_class.construct(app, connection)
		svc.add_connection(connection_instance)


	def construct_lookups(self, app, svc):
		lookups = self.Definition.get('lookups')
		if lookups is None:
			return

		for i in range(0, len(lookups)):
			lookup_definition = lookups[i]
			self.construct_lookup(app, svc, lookup_definition)


	def construct_lookup(self, app, svc, lookup):
		svc = app.get_service("bspump.PumpService")
		module = importlib.import_module(lookup["module"])
		lookup_class = getattr(module, lookup["class"])
		lookup_instance = lookup_class.construct(app, lookup)
		svc.add_lookup(lookup_instance)


	def construct_pipelines(self, app, svc):
		pipelines = self.Definition.get('pipelines')
		if pipelines is None:
			return

		for i in range(0, len(pipelines)):
			pipeline_definition = pipelines[i]
			self.construct_pipeline(app, svc, pipeline_definition)


	def construct_pipeline(self, app, svc, pipeline_definition):
		svc = app.get_service("bspump.PumpService")
		pipeline_id = pipeline_definition["id"]
		pipeline = Pipeline(app, pipeline_id)

		sources_definition = pipeline_definition["sources"]
		processors_definition = pipeline_definition.get("processors")
		sink_definition = pipeline_definition["sink"]

		sources = self.construct_sources(app, svc, pipeline, sources_definition)
		pipeline.set_source(sources)
		processors = self.construct_processors(app, svc, pipeline, processors_definition)
		sink = self.construct_processor(app, svc, pipeline, sink_definition)

		processors.append(sink)
		for processor in processors:
			pipeline.append_processor(processor)

		svc.add_pipeline(pipeline)


	def construct_sources(self, app, svc, pipeline, definition):

		sources = []
		for i in range(0, len(definition)):
			source_definition = definition[i]
			source = self.construct_source(app, svc, pipeline, source_definition)
			sources.append(source)

		return sources


	def construct_source(self, app, svc, pipeline, definition):
		module = importlib.import_module(definition["module"])
		processor_class = getattr(module, definition["class"])
		processor = processor_class.construct(app, pipeline, definition)
		trigger_definition = definition.get("trigger")
		if trigger_definition is None:
			return processor
		trigger = self.construct_trigger(app, svc, trigger_definition)
		return processor.on(trigger)


	def construct_trigger(self, app, svc, definition):
		module = importlib.import_module(definition["module"])
		trigger_class = getattr(module, definition["class"])
		trigger = trigger_class.construct(app, definition)
		return trigger


	def construct_processors(self, app, svc, pipeline, definition):
		if definition is None:
			return []

		processors = []
		for i in range(0, len(definition)):
			processor_definition = definition[i]
			processor = self.construct_processor(app, svc, pipeline, processor_definition)
			processors.append(processor)

		return processors


	def construct_processor(self, app, svc, pipeline, definition):
		module = importlib.import_module(definition["module"])
		processor_class = getattr(module, definition["class"])
		processor = processor_class.construct(app, pipeline, definition)
		return processor
