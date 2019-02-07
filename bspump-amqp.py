#!/usr/bin/env python3
import bspump
import bspump.socket
import bspump.common
import bspump.amqp
import bspump.file
import bspump.trigger


class SamplePipeline1(bspump.Pipeline):

	'''
	To test this pipeline, use:
	nc -v 127.0.0.1 7000
	'''

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.socket.TCPSource(app, self),
			bspump.amqp.AMQPSink(app, self, "AMQPConnection1")
		)


class SamplePipeline2(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.amqp.AMQPSource(app, self, "AMQPConnection1", config={'queue': 'teskalabs.q'}),
			bspump.common.NullSink(app, self)
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
