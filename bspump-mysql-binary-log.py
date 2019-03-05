from bspump.mysql import MySQLBinaryLogSource, MySQLConnection

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
		svc.add_pipeline(MyPipeline(self))
		

class MyPipeline(Pipeline):
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.mysql.MySQLBinaryLogSource(app, self, "MySQLConnection",
				config={'server_id': 1}
			).on(
				bspump.trigger.PubSubTrigger(app, "runmysqlpipeline!")
			),
			PPrintSink(app, self)
		)



if __name__ == '__main__':
	app = MyApplication()
	app.PubSub.publish("runmysqlpipeline!", asynchronously=True)
	app.run()
