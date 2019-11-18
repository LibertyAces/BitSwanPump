import bspump
import bspump.common
import bspump.netflow


class NetFlowPipeline(bspump.Pipeline):
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.netflow.NetFlowSource(app, self, config={}),
			bspump.common.JsonBytesToDictParser(app, self),
			bspump.common.PPrintSink(app, self),
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	my_pipeline = NetFlowPipeline(app, 'NetFlowPipeline')
	svc.add_pipeline(my_pipeline)

	app.run()
