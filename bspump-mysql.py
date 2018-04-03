#!/usr/bin/env python3
import logging
import asyncio
import asab
import bspump
import bspump.socket
import bspump.common
import bspump.influxdb
import bspump.mysql

###

L = logging.getLogger(__name__)

###

class Encryptor(bspump.Processor):
	def process(self, event):
		event["name"] = event["name"]+"encrypted!"
		return event

class Decryptor(bspump.Processor):
	def process(self, event):
		event["name"] = event["name"][:-len("encrypted!")]
		return event

class SamplePipeline(bspump.Pipeline):

	'''
	Test this pipeline by
	$ echo 'metrix,tag1=value1,tag2=value2 value=1 1434055562000000000' |  nc localhost 7000
	'''

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.mysql.MySQLSource(app, self, "MySQLConnection1", config={
				'query':'SELECT id, name FROM pet WHERE enc=true;'}),
			Decryptor(app, self),
			bspump.mysql.MySQLSink(app, self, "MySQLConnection1", config={
				'query': 'UPDATE pet SET enc=true, name={name} WHERE id={id}'
				})
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_connection(
		bspump.mysql.MySQLConnection(app, "MySQLConnection1")
	)

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()
