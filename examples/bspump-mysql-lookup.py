from bspump.mysql import MySQLLookup, MySQLConnection

from bspump.file import FileCSVSource
from bspump.trigger import OpportunisticTrigger
from bspump.common import PPrintSink
from bspump import BSPumpApplication, Pipeline, Processor
import logging
import bspump.common

##
L = logging.getLogger(__name__)
##

class MyApplication(BSPumpApplication):
	def __init__(self):
		super().__init__()

		svc = self.get_service("bspump.PumpService")

		mysql_connection = MySQLConnection(self, "MySQLConnection", config={
			"user":"user",
			"password":"password",
			"db":"users"
		})

		svc.add_connection(mysql_connection)
		# mysql_connection.
		# print(">>>>>", mysql_connection.acquire())
		
		self.MySQLLookup =  MySQLLookup(self, "MySQLLookup", 
			mysql_connection=mysql_connection,
			config={
				'from': 'user_loc',
				'key': 'user'
			})

		svc.add_lookup(self.MySQLLookup)
		svc.add_pipeline(MyPipeline(self))
		

class MyPipeline(Pipeline):
	# Enriches the event with location from ES lookup
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		self.build(
			FileCSVSource(app, self, 
				config={"post":"noop", "path":"bspump/mysql/var/users.csv"}
				).on(OpportunisticTrigger(app)),
			MyProcessor(app, self), 
			PPrintSink(app, self)
		)


class MyProcessor(Processor):

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		svc = app.get_service("bspump.PumpService")
		self.Lookup = svc.locate_lookup("MySQLLookup")

	
	def process(self, context, event):
		if 'user' not in event:
			return None

		info = self.Lookup.get(event['user'])
		if info is not None:
			event['L'] = {'lat':info.get('lat'), 'lon':info.get('lat')}
		
		return event


if __name__ == '__main__':
	app = MyApplication()
	app.run()
