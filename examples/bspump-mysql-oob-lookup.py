import logging

import bspump
import bspump.common
import bspump.file
import bspump.mysql
import bspump.trigger

##

L = logging.getLogger(__name__)

##


class MyApplication(bspump.BSPumpApplication):
	"""
	The following example illustrates usage of MySQLLookup with OOBEnricher,
	so the write-through cache loading, which may take some time,
	is processed asynchronously.

	## Try it out

		$ docker run --rm -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root_password mysql

	Insert some sample data in your database
	```
		mysql> create database users;
		mysql> use users;
		mysql> CREATE TABLE user_loc (id INT NOT NULL AUTO_INCREMENT, user CHAR(30), lat FLOAT(9,6), lon FLOAT(9,6), PRIMARY KEY (id));
		mysql> INSERT INTO user_loc (user, lat, lon) VALUES ("user_0", 37.405992,-122.078515),("user_1", 50.08804, 14.42076);
	```
	"""

	def __init__(self):
		super().__init__()

		svc = self.get_service("bspump.PumpService")

		mysql_connection = bspump.mysql.MySQLConnection(self, "MySQLConnection", config={
			"user": "root",
			"password": "root_password",
			"db": "users"
		})

		svc.add_connection(mysql_connection)

		self.MySQLLookup = bspump.mysql.MySQLLookup(self, connection=mysql_connection, id="MySQLLookup", config={
			'from': 'user_loc',
			'key': 'user',
		})

		svc.add_lookup(self.MySQLLookup)
		svc.add_pipeline(MyPipeline(self))


class LatLonEnricher(bspump.Processor):

	def process(self, context, event):
		info = event.get("info")
		if info is not None:
			event['L'] = {'lat': info.get('lat'), 'lon': info.get('lon')}
			del event['info']
		return event


class MyPipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.file.FileCSVSource(app, self, config={
				"post": "noop",
				"path": "./data/users.csv"
			}).on(bspump.trigger.OpportunisticTrigger(app)),
			bspump.common.OOBLookupEnricher(app, self, "MySQLLookup", config={
				"input_key": "user", "output_key": "info"
			}),
			LatLonEnricher(app, self),
			bspump.common.PPrintSink(app, self)
		)


if __name__ == '__main__':
	app = MyApplication()
	app.run()
