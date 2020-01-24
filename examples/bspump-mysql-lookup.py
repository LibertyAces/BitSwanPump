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
	The following example illustrates usage of MySQLLookup with AsyncEnricher,
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
			"db": "users",
		})

		svc.add_connection(mysql_connection)

		self.MySQLLookup = bspump.mysql.MySQLLookup(self, connection=mysql_connection, id="MySQLLookup", config={
			'from': 'user_loc',
			'key': 'user',
		})

		svc.add_lookup(self.MySQLLookup)
		svc.add_pipeline(MyPipeline(self))


class MyPipeline(bspump.Pipeline):
	# Enriches the event with location from ES lookup
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.file.FileCSVSource(app, self, config={
				"post": "noop",
				"path": "./data/users.csv"
			}).on(bspump.trigger.OpportunisticTrigger(app)),
			MyEnricher(app, self),
			bspump.common.PPrintSink(app, self)
		)


class MyEnricher(bspump.Generator):

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		svc = app.get_service("bspump.PumpService")
		self.Lookup = svc.locate_lookup("MySQLLookup")

	async def generate(self, context, event, depth):
		if 'user' not in event:
			return None

		info = await self.Lookup.get(event['user'])
		if info is not None:
			event['L'] = {'lat': info.get('lat'), 'lon': info.get('lon')}

		# Inject a new event into a next depth of the pipeline
		self.Pipeline.inject(context, event, depth)


if __name__ == '__main__':
	app = MyApplication()
	app.run()
