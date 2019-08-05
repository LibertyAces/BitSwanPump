import logging

import bspump
import bspump.common
import bspump.mysql
import bspump.mysql.binlogsource

##

L = logging.getLogger(__name__)


##


class MyApplication(bspump.BSPumpApplication):
	def __init__(self):
		super().__init__()

		svc = self.get_service("bspump.PumpService")

		mysql_connection = bspump.mysql.MySQLConnection(self, "MySQLConnection", config={
			"user": "user",
			"password": "password",
			"db": "users"
		})

		svc.add_connection(mysql_connection)
		svc.add_pipeline(MyPipeline(self))


class MyPipeline(bspump.Pipeline):
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.mysql.binlogsource.MySQLBinaryLogSource(app, self, "MySQLConnection", config={
				'server_id': 1,
				'log_file': 'mysql-bin.000001'
			}),
			bspump.common.PPrintSink(app, self)
		)


if __name__ == '__main__':
	app = MyApplication()
	app.run()
