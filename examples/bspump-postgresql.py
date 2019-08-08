#!/usr/bin/env python3
import logging

import bspump
import bspump.common
import bspump.file
import bspump.postgresql
import bspump.trigger

###

L = logging.getLogger(__name__)

###


class SamplePipeline(bspump.Pipeline):
	"""
	## Try it

	# Create PostgresSQL database
	$ docker run --rm -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres

	# Initialize database

	$ docker run -it --rm --network host postgres psql -h localhost -U postgres
	```
		CREATE DATABASE test_countries;
		\c test_countries;
		CREATE TABLE countries (id SERIAL PRIMARY KEY, country VARCHAR (2) UNIQUE NOT NULL, position INT NOT NULL);
	```
	"""
	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.Sink = bspump.postgresql.PostgreSQLSink(app, self, "PostgreSQLConnection", config={
			'query': 'INSERT INTO countries (country, position) VALUES (%s, %s);',
			'data': 'Country,Position'
		})

		self.build(
			bspump.file.FileCSVSource(app, self, config={
				'path': './data/sample.csv',
				'delimiter': ';',
				'post': 'noop'
			}).on(bspump.trigger.RunOnceTrigger(app)),

			bspump.common.PPrintProcessor(app, self),
			self.Sink,
		)


if __name__ == '__main__':
	
	app = bspump.BSPumpApplication()
	svc = app.get_service("bspump.PumpService")

	# Create connection
	svc.add_connection(
		bspump.postgresql.PostgreSQLConnection(app, "PostgreSQLConnection", config={
			'host': 'localhost',
			'user': 'postgres',
			'password': 'postgres',
			'db': 'test_countries',
		})
	)

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	# This is how pipeline is triggered:
	app.PubSub.publish("runpostgresqlpipeline!", asynchronously=True)

	app.run()
