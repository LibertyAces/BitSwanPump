import bspump
import bspump.common
import bspump.subprocess


class NetFlowPipeline(bspump.Pipeline):
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.subprocess.SubProcessSource(app, self, config={
				'command': 'tshark -l -n -T ek -i wlan0'
			}),
			bspump.common.StdJsonToDictParser(app, self),
			bspump.common.PPrintSink(app, self),
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	my_pipeline = NetFlowPipeline(app, 'NetFlowPipeline')
	svc.add_pipeline(my_pipeline)

	app.run()
