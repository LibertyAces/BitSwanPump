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

	def __init__(self, app, pipeline_id, lookup):
		super().__init__(app, pipeline_id)

		self.Lookup = lookup

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
	lkp = svc.ensure_lookup(MyDictionaryLookup)

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline', lkp)
	svc.add_pipeline(pl)

	app.run()
