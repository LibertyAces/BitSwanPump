from bspump import BSPumpApplication, Pipeline
import bspump.trigger
import bspump.common
import bspump.postgresql
import logging



##
L = logging.getLogger(__name__)
##


class MyApplication(BSPumpApplication):
	def __init__(self):
		super().__init__()
		svc = self.get_service("bspump.PumpService")
		svc.add_connection(bspump.postgresql.PostgreSQLConnection(self, config={'user':'postgres', 'password':'secretpass', 'db':'users'}))
		svc.add_pipeline(MyPipeline0(self))
		

class MyPipeline0(Pipeline):
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.postgresql.PostgreSQLLogicalReplicationSource(app, self, 
				"PostgreSQLConnection", 
				config={'slot_name':'pytest', 'output_plugin':"test_decoding"}),
			bspump.common.PPrintSink(app, self)
		)


if __name__ == '__main__':
	app = MyApplication()
	app.run()
