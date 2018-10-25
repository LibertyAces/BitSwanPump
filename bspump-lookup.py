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
		self.Lookup = svc.locate_lookup("MyDictionaryLookup")

		self.build(
			bspump.file.FileCSVSource(app, self, config={'path': './examples/data/sample.csv', 'delimiter': ';'})
				.on(bspump.trigger.RunOnceTrigger(app)),
			bspump.common.PPrintSink(app, self),
		)


class MyDictionaryLookup(bspump.DictionaryLookup):

	async def load(self):
		self.Dictionary = bspump.load_json_file('./examples/data/country_names.json')


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	# Construct the lookup
	lkp = svc.add_lookup(MyDictionaryLookup(app, "MyDictionaryLookup"))

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()
