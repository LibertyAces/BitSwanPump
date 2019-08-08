#!/usr/bin/env python3
import logging

import bspump
import bspump.common
import bspump.mysql
import bspump.trigger

###

L = logging.getLogger(__name__)

###


class ReverseProcessor(bspump.Processor):
	def process(self, context, event):
		for key in event.keys():
			if isinstance(event[key], str):
				event[key] = event[key][::-1]
		return event


class ToggleCaseProcessor(bspump.Processor):
	def process(self, context, event):
		for key in event.keys():
			if isinstance(event[key], str):
				if event[key].islower():
					event[key] = event[key].upper()
				else:
					event[key] = event[key].lower()
		return event


class SamplePipeline(bspump.Pipeline):
	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.Sink = bspump.mysql.MySQLSink(app, self, "MySQLConnection1", config={
			'query': 'UPDATE people SET name=%s, surname=%s WHERE id=%s;',
			'data': 'name,surname,id'
		})

		self.build(

			bspump.mysql.MySQLSource(app, self, "MySQLConnection1", config={
				'query': 'SELECT id, name, surname FROM people;'
			}).on(bspump.trigger.PubSubTrigger(app, "RunMySQLPipeline!")),

			ReverseProcessor(app, self),
			ToggleCaseProcessor(app, self),
			bspump.common.PPrintProcessor(app, self),
			self.Sink,
		)


if __name__ == '__main__':
	"""
	This is a sample bspump application with pipeline that implements MySQL source and sink

	## Try it out

		$ docker run --rm -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root_password mysql
		
	Insert some sample data in your database
	```
		mysql> create database sample_db;
		mysql> use sample_db;
		mysql> CREATE TABLE people (id INT NOT NULL AUTO_INCREMENT, name CHAR(30), surname CHAR(30), PRIMARY KEY (id));
		mysql> INSERT INTO people (name, surname) VALUES ("john", "doe"),("juan", "perez"),("wop", "wops");
	```

	"""
	app = bspump.BSPumpApplication()
	svc = app.get_service("bspump.PumpService")

	# Create connection
	svc.add_connection(
		bspump.mysql.MySQLConnection(app, "MySQLConnection1", config={
			"user": "root",
			"password": "root_password",
			"db": "sample_db",
		})
	)

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	# This is how pipeline is triggered:
	app.PubSub.publish("RunMySQLPipeline!", asynchronously=True)

	app.run()
