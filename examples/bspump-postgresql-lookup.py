import logging

import bspump
import bspump.common
import bspump.file
import bspump.postgresql
import bspump.trigger
##

L = logging.getLogger(__name__)


##

class MyApplication(bspump.BSPumpApplication):
	"""
	The following example illustrates usage of PostgreSQLLookup with AsyncEnricher,
	so the write-through cache loading, which may take some time,
	is processed asynchronously.

	## Try it out

		$ docker run --rm -p 5432:5432 -e POSTGRES_PASSWORD=password postgres
		$ psql -p 5432 -h localhost -U postgres

	Insert some sample data in your database
	```
		psql> create database users;
		psql> \c users
		psql> CREATE TABLE user_loc (id SERIAL, username VARCHAR, lat float(9), lon float(9), PRIMARY KEY (id)); # user is a keyword in PGSQL
		psql> INSERT INTO user_loc (username, lat, lon) VALUES ('user_0', 37.405992,-122.078515),('user_1', 50.08804, 14.42076);
	```
	"""

	def __init__(self):
		super().__init__()

		svc = self.get_service("bspump.PumpService")

		pgsql_connection = bspump.postgresql.PostgreSQLConnection(self, "PostgreSQLConnection", config={
				'host': '127.0.0.1',
				'user': 'postgres',
				'password': 'password',
				'db': 'users',
			})

		svc.add_connection(pgsql_connection)

		self.postgres_lookup = bspump.postgresql.PostgreSQLLookup(self, connection=pgsql_connection,
																  id="PostgreSQLLookup", config={
				'from': 'user_loc',
				'key': 'username',
			})

		svc.add_lookup(self.postgres_lookup)
		svc.add_pipeline(MyPipeline(self))


class MyPipeline(bspump.Pipeline):
	# Enriches the event with location from PostgreSQL lookup
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
		self.Lookup = svc.locate_lookup("PostgreSQLLookup")

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
