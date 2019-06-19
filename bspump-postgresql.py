#!/usr/bin/env python3
import logging
import asyncio
import asab
import bspump
import bspump.postgresql
import bspump.trigger
import bspump.file
import bspump.common

###

L = logging.getLogger(__name__)

###


class SamplePipeline(bspump.Pipeline):
	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.Sink = bspump.postgresql.PostgreSQLSink(app, self, "PostgreSQLConnection", config={
			'query': 'INSERT INTO test (country, position) VALUES (%s, %s);',
			'data': 'Country,Position'
		})

		self.build(
			bspump.file.FileCSVSource(
				app, self, config={'path': 'examples/data/sample.csv', 'delimiter': ';', 'post': 'noop'}
			).on(bspump.trigger.RunOnceTrigger(app)),
			bspump.common.PPrintProcessor(app, self),
			self.Sink,
		)


if __name__ == '__main__':
	
	app = bspump.BSPumpApplication()
	svc = app.get_service("bspump.PumpService")

	# Create connection
	svc.add_connection(
		bspump.postgresql.PostgreSQLConnection(app, "PostgreSQLConnection")
	)

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	# This is how pipeline is triggered:
	app.PubSub.publish("runpostgresqlpipeline!", asynchronously=True)

	app.run()
