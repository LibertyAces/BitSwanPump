#!/usr/bin/env python3
import logging
import asyncio
import asab
import bspump
import bspump.socket
import bspump.common
from bspump.elasticsearch import ElasticSearchSink
from bspump.elasticsearch import ElasticSearchDriver
from bspump import Source 

###

L = logging.getLogger(__name__)

###

class SampleSource(Source):
	def __init__(self, app, pipeline):
		super().__init__(app, pipeline)

	async def start(self):
		try:
			self.process({
				"@timestamp": "timestamp",
				"message": "blablabla",
			})
		except:
			L.exeption("Error in pipeline")

class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.set_source(SampleSource(app, self))
		self.append_processor(ElasticSearchSink(app, self, driver=ElasticSearchDriver(app)))


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'mypipeline')
	svc.add_pipeline(pl)

	app.run()
