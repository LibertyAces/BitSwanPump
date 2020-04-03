import json
import yaml
import importlib
import glob
import os
import logging

import asab

import bspump.analyzer

##

L = logging.getLogger(__name__)

##

asab.Config.add_defaults(
	{
		"SegmentBuilder": {
			"path": "./etc/processors/*.json",
		},
	}
)


class SegmentBuilder(object):
	"""
	SegmentBuilder is meant to add a new segment to the pipeline,
	that consists of processors such as enrichers, analyzers etc.

	Usage:

		self.SegmentBuilder = bspump.SegmentBuilder()
		self.SegmentBuilder.construct_segment(self)
	"""

	def __init__(self):
		self.Path = asab.Config["SegmentBuilder"]["path"]
		self.DefinitionsLookups = []
		self.DefinitionsProcessors = []
		file_list = glob.glob(self.Path, recursive=True)
		while len(file_list) > 0:
			file_name = file_list.pop(0)
			if os.path.isfile(file_name):
				with open(file_name) as file:
					if file_name.endswith(".yml"):
						# Read YML file
						definition = yaml.load(file)
					else:
						# Read JSON file
						definition = json.load(file)
					if definition["class"].endswith("Lookup"):
						self.DefinitionsLookups.append(definition)
					else:
						self.DefinitionsProcessors.append(definition)

	def construct_segment(self, app):
		svc = app.get_service("bspump.PumpService")

		# First create lookups
		for definition in self.DefinitionsLookups:
			pipeline = svc.locate(definition["pipeline_id"])
			enricher = self.construct_enricher_lookup(app, pipeline, definition)
			if enricher is not None:
				sink = pipeline.Processors[-1].pop()
				pipeline.append_processor(enricher)
				pipeline.append_processor(sink)
				self.build_profiling(pipeline, enricher)

		# Then create other processors
		for definition in self.DefinitionsProcessors:
			pipeline = svc.locate(definition["pipeline_id"])
			processor = self.construct_processor(app, pipeline, definition)
			if processor is not None:
				sink = pipeline.Processors[-1].pop()
				pipeline.append_processor(processor)
				pipeline.append_processor(sink)
				self.build_profiling(pipeline, processor)

	def construct_enricher_lookup(self, app, pipeline, definition):
		svc = app.get_service("bspump.PumpService")

		# Construct the lookup first
		_module = importlib.import_module(definition["module"])
		_class = getattr(_module, definition["class"])
		lookup_instance = _class.construct(app, definition)
		svc.add_lookup(lookup_instance)

		# Construct enricher for newly created lookup
		_class = getattr(_module, "{}Enricher".format(definition["class"]))
		enricher_instance = _class.construct(app, pipeline, lookup_instance, definition)
		return enricher_instance

	def construct_processor(self, app, pipeline, definition):
		_module = importlib.import_module(definition["module"])
		_class = getattr(_module, definition["class"])
		processor = _class.construct(app, pipeline, definition)
		return processor

	def build_profiling(self, pipeline, processor):
		pipeline.ProfilerCounter[processor.Id] = pipeline.MetricsService.create_counter(
			'bspump.pipeline.profiler',
			tags={
				'processor': processor.Id,
				'pipeline': pipeline.Id,
			},
			init_values={'duration': 0.0, 'run': 0},
			reset=pipeline.ResetProfiler,
		)
		if isinstance(processor, bspump.analyzer.Analyzer):
			pipeline.ProfilerCounter['analyzer_' + processor.Id] = pipeline.MetricsService.create_counter(
				'bspump.pipeline.profiler',
				tags={
					'analyzer': processor.Id,
					'pipeline': pipeline.Id,
				},
				init_values={'duration': 0.0, 'run': 0},
				reset=pipeline.ResetProfiler,
			)
