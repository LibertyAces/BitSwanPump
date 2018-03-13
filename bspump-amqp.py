#!/usr/bin/env python3
import bspump
import bspump.socket
import bspump.common
import bspump.amqp

class SamplePipeline1(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.socket.TCPStreamSource(app, self),
			bspump.amqp.AMQPSink(app, self, "AMQPConnection1")
		)

class SamplePipeline2(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.amqp.AMQPSource(app, self, "AMQPConnection1"),
			bspump.common.PPrintSink(app, self)
		)

if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_connection(
		bspump.amqp.AMQPConnection(app, "AMQPConnection1")
	)

	svc.add_pipelines(
		SamplePipeline1(app, "SamplePipeline1"),
		SamplePipeline2(app, "SamplePipeline2"),
	)

	app.run()
