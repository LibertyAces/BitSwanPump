#!/usr/bin/env python3
import logging
import asyncio
import asab
import bspump
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
			'query': 'UPDATE people SET name={name}, surname={surname} WHERE id={id};'
		})

		self.build(
			bspump.mysql.MySQLSource(app, self, "MySQLConnection1",
				config={'query':'SELECT id, name, surname FROM people;'}
			).on(
				bspump.trigger.PubSubTrigger(app, "runmysqlpipeline!")
			),
			ReverseProcessor(app, self),
			ToggleCaseProcessor(app, self),

		)

		self.PubSub.subscribe("bspump.pipeline.cycle_end!", self.on_cycle_end)


	def on_cycle_end(self, event_name, pipeline):
		'''
		This ensures that at the end of the file scan, the target file is closed
		'''
		self.Sink.rotate()


if __name__ == '__main__':
	""" This is a sample bspump application with pipeline that implements MySQL source and sink

		## Try it out
		
		Insert some sample data in your database
		```
			mysql> create database sampledb;
			mysql> use sampledb;
			mysql> CREATE TABLE people (id MEDIUMINT NOT NULL AUTO_INCREMENT,name CHAR(30), surname CHAR(30), PRIMARY KEY (id));
			mysql> INSERT INTO people (name, surname) VALUES ("john", "doe"),("juan", "perez"),("wop", "wops");
		```

		Configure bspump in `./etc/site.conf`
		```
			[connection:MySQLConnection1]
			user=username
			password=password
			db=sampledb
		```
		
		To use chunking, just change default 'rows_in_chunk' from 1 to something else
		and use query with variable 'chunk':
		```
			[sink:MySQLSink]
			rows_in_chunk=40
			query='INSERT INTO people (name, surname) VALUES {chunk}'
		```

		Run bspump
		```
		./bspump-mysql.py -c ./etc/site.conf
		```

);
	"""
	app = bspump.BSPumpApplication()
	svc = app.get_service("bspump.PumpService")

	# Create connection
	svc.add_connection(
		bspump.mysql.MySQLConnection(app, "MySQLConnection1")
	)

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	# This is how pipeline is triggered:
	app.PubSub.publish("runmysqlpipeline!", asynchronously=True)

	app.run()
