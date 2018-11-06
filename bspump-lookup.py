#!/usr/bin/env python3
import logging
import asyncio
import asab
import bspump
import bspump.file
import bspump.common
import bspump.trigger
import pprint

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
					'path': './examples/data/sample.csv',
					'delimiter': ';',
					'post': 'noop'}
				)
				.on(bspump.trigger.PubSubTrigger(app, "go!", self.PubSub)),
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


class MyDictionaryLookup(bspump.DictionaryLookup):

	async def load(self):
		# Called only when we are master (no master_url provided)
		self.set(bspump.load_json_file('./examples/data/country_names.json'))
		return True


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
	lkp = svc.add_lookup(MyDictionaryLookup(app, "MyDictionaryMasterLookup"))
	lkps = svc.add_lookup(MyDictionaryLookup(app, "MyDictionarySlaveLookup", config={
		'master_url': 'http://localhost:8083/',
		'master_lookup_id': 'MyDictionaryMasterLookup'
	}))

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()
