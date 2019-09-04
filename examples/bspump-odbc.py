#!/usr/bin/env python3
import logging
import asyncio
import asab
import bspump
import bspump.odbc
import bspump.trigger
import bspump.common

###

L = logging.getLogger(__name__)

###

class SideSwitchProcessor(bspump.Processor):

	def process(self, context, event):
		side = event.get("side")
		if side == "DARK":
			event["side"] = "LIGHT"
		else:
			event["side"] = "DARK"
		return event



class SamplePipeline(bspump.Pipeline):
	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.odbc.ODBCSource(app, self, "ODBCConnection1",
				config={'query':'SELECT first_name, last_name, side FROM characters;'}
			).on(
				bspump.trigger.PubSubTrigger(app, "runodbcpipeline!")
			),
			bspump.common.PPrintProcessor(app, self),
			SideSwitchProcessor(app, self),
			bspump.common.PPrintSink(app, self),
		)


if __name__ == '__main__':
	"""
	This is a bspump odbc application example. Follow these steps to run the app:
	

	Create table and insert data
		```
			mysql> create database sampledb;
			mysql> use sampledb;
			mysql> CREATE TABLE characters (id MEDIUMINT NOT NULL AUTO_INCREMENT,first_name VARCHAR(30), last_name VARCHAR(30), side VARCHAR(30), PRIMARY KEY (id));
			mysql> INSERT INTO characters (first_name, last_name, side) VALUES ("obi-wan", "kenobi", "LIGHT"),("luke", "skywalker", "LIGHT"),("darth", "vader", "DARK"),("darth", "sidious", "DARK");
		```

		Configure bspump in `./etc/site.conf`
		```
			[connection:ODBCConnection1]
			user=username
			password=password
			db=sampledb
			driver=MySQL ODBC 8.0 Unicode Driver
			db=sampledb
		```

		Run bspump
		```
		./bspump-odbc.py -c ./etc/site.conf
		```


	"""
	app = bspump.BSPumpApplication()
	svc = app.get_service("bspump.PumpService")

	# Create connection
	svc.add_connection(
		bspump.odbc.ODBCConnection(app, "ODBCConnection1")
	)

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	# This is how pipeline is triggered:
	app.PubSub.publish("runodbcpipeline!", asynchronously=True)

	app.run()
