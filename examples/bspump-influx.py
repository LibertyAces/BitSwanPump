#!/usr/bin/env python3
import logging

import bspump
import bspump.common
import bspump.influxdb
import bspump.socket

###

L = logging.getLogger(__name__)

###


class SamplePipeline(bspump.Pipeline):

	"""
	Setup influx in docker
		$ docker run -p 8086:8086 -e INFLUXDB_DB=mydb influxdb

	Test this pipeline by
		$ echo 'metrix,tag1=value1,tag2=value2 value=1 1434055562000000000' |  nc localhost 7000
	"""

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.socket.TCPStreamSource(app, self, config={'port': 7000}),
			bspump.common.PPrintProcessor(app, self),
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
