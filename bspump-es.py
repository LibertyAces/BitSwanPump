#!/usr/bin/env python3
import logging
import asyncio
import asab
import bspump
import bspump.socket
import bspump.common
import bspump.elasticsearch

###

L = logging.getLogger(__name__)

###

class SamplePipeline(bspump.Pipeline):

	'''
	Test this pipeline by
	$ echo '{"Ahoj":"svete"}' |  nc localhost 7000
	'''

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.socket.FileLineSource(app, self,).on(bspump.trigger.RunOnceTrigger(app)),
			bspump.common.JSONParserProcessor(app, self),
			bspump.elasticsearch.ElasticSearchSink(app, self, "ESConnection1")
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_connection(
		bspump.elasticsearch.ElasticSearchConnection(app, "ESConnection1")
	)

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()
