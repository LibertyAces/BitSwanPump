#!/usr/bin/env python3
import logging
import asyncio
import asab
import bspump
import bspump.socket
import bspump.common
import bspump.influxdb

###

L = logging.getLogger(__name__)

###

class SamplePipeline(bspump.Pipeline):

	'''
	Test this pipeline by
	$ echo 'metrix,tag1=value1,tag2=value2 value=1 1434055562000000000' |  nc localhost 7000
	'''

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.socket.TCPStreamSource(app, self, config={'port': 7000}),
			bspump.influxdb.InfluxDBSink(app, self, "InfluxConnection1")
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_connection(
		bspump.influxdb.InfluxDBConnection(app, "InfluxConnection1")
	)

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()
