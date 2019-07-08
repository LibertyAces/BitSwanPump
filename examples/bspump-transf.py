#!/usr/bin/env python3
import logging
import asyncio
import asab
import bspump
import bspump.file
import bspump.common
import bspump.trigger

###

L = logging.getLogger(__name__)

###

class MyTransformator(bspump.common.MappingTransformator):

	def build(self, app):
		return {
			'color': self.color,
			'category': self.category,
		}

	def color(self, key, value):
		return key.upper(), 1.0

	def category(self, key, value):
		return key, value.upper()

#

class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.file.FileJSONSource(app, self, config={'path': './data/sample.json', 'post': 'noop',})
				.on(bspump.trigger.PubSubTrigger(app, "Application.tick!")),
			MyTransformator(app, self),
			bspump.common.MappingItemsProcessor(app, self),
#			bspump.common.IteratorGenerator(app, self),
			bspump.common.PPrintSink(app, self),
		)

###

if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()
