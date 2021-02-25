#!/usr/bin/env python3
import logging
import io
import json

import bspump
import bspump.common
import bspump.file
import bspump.trigger

###

L = logging.getLogger(__name__)

###


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


class MyDictionaryLookup(bspump.Lookup):
	def __init__(self, app, id=None, config=None, lazy=False):
		self.Dictionary = {}
		super().__init__(app, id, config=config, lazy=lazy)

	def deserialize(self, data):
		# f = io.BytesIO(data)
		# print(data)
		if data:
			self.Dictionary.update(json.loads(data.decode('utf-8')))

	def __getitem__(self, item):
		return self.Dictionary.get(item, None)


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

	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	# Construct lookups (in master/slave configuration)
	lkp = svc.add_lookup(MyDictionaryLookup(
		app,
		"MyDictionaryMasterLookup",
		config={"source_url": "./data/country_names.json"}
	))
	lkps = svc.add_lookup(MyDictionaryLookup(app, "MyDictionarySlaveLookup", config={
		'master_url': 'http://localhost:8083/',
		'master_lookup_id': 'MyDictionaryMasterLookup'
	}))

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()
