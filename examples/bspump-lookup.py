#!/usr/bin/env python3
import json
import logging
import time

import bspump
import bspump.common
import bspump.file
import bspump.http
import bspump.trigger

###

L = logging.getLogger(__name__)

###


"""
This example demonstrates the usage of bspump.Lookup in master and slave mode.

Expected behaviour:
1) Initialize App, Pipeline, master Lookup and slave Lookup.
2) Slave Lookup fails to retrieve lookup data, because master is not fully loaded yet. 
	The pipeline waits for a "go!" message to run.
3) Master finishes loading.
4) On next App tick, slave lookup is reloaded, retrieves lookup data and emits a "go!" message.
5) The pipeline triggers, runs and finishes.
"""


class SampleApplication(bspump.BSPumpApplication):
	def __init__(self):
		super().__init__()
		self.PumpService = self.get_service("bspump.PumpService")
		self.Lookup = None
		self.PubSub.subscribe("Application.tick/10!", self.reload_lookups)

	async def reload_lookups(self, event_type):
		if self.Lookup is not None:
			self.Lookup.ensure_future_update(self.Loop)


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		svc = app.get_service("bspump.PumpService")
		self.Lookup = svc.locate_lookup("MyDictionarySlaveLookup")

		self.Lookup.PubSub.subscribe("bspump.Lookup.changed!", self.lookup_updated)
		self.PubSub.subscribe("bspump.pipeline.cycle_end!", self.cycle_end)
		self.RunCountdown = 1

		self.build(
			bspump.file.FileCSVSource(app, self, config={
				'path': './data/sample.csv',
				'delimiter': ';',
				'post': 'noop'
			}).on(bspump.trigger.PubSubTrigger(app, "go!", self.PubSub)),
			LookupTransformator(app, self, self.Lookup),
			bspump.common.PPrintSink(app, self),
		)

	def lookup_updated(self, event_name):
		# We have a lookup, so we can start pipeline
		if self.RunCountdown == 1:
			self.RunCountdown -= 1
			self.PubSub.publish("go!")

	def cycle_end(self, event_name, pipeline):
		# The file is processed, halt the application
		svc = app.get_service("bspump.PumpService")
		svc.App.stop()


class LookupTransformator(bspump.Processor):

	def __init__(self, app, pipeline, lookup, id=None, config=None):
		super().__init__(app=app, pipeline=pipeline, id=id, config=config)
		self.Lookup = lookup

	def process(self, context, event):
		event['Country'] = self.Lookup.get(event['Country'])
		return event


if __name__ == '__main__':
	'''
	Run with Web API enabled:

	/bspump-lookup.py -w 0.0.0.0:8083
	'''

	app = SampleApplication()

	svc = app.get_service("bspump.PumpService")

	lkp = svc.add_lookup(bspump.DictionaryLookup(app, "MyDictionaryMasterLookup", config={
		"source_url": "./data/country_names.json",
		"use_cache": "no"
	}))

	lkps = svc.add_lookup(bspump.DictionaryLookup(app, "MyDictionarySlaveLookup", config={
		"source_url": "http://localhost:8083/bspump/v1/lookup/MyDictionaryMasterLookup",

		# Backwards-compatible configuration:
		# "master_url": "http://localhost:8083/",
		# "master_url_endpoint": "/bspump/v1/lookup",
		# "master_lookup_id": 'MyDictionaryMasterLookup',
		"use_cache": "no"
	}))

	app.Lookup = lkps

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()
