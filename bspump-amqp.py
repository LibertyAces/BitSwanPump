#!/usr/bin/env python3
import asyncio
import asab
import bspump
import bspump.socket
import bspump.common
import bspump.amqp


class SamplePipeline1(bspump.Pipeline):

	def __init__(self, app, pipeline_id, driver):
		super().__init__(app, pipeline_id)

		self.driver = driver

		self.construct(
			bspump.socket.TCPStreamSource(app, self),
			bspump.amqp.AMQPSink(app, self, self.driver)
		)


class SamplePipeline2(bspump.Pipeline):

	def __init__(self, app, pipeline_id, driver):
		super().__init__(app, pipeline_id)

		self.driver = driver

		self.construct(
			bspump.amqp.AMQPSource(app, self, self.driver),
			bspump.common.PPrintSink(app, self)
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	amqp_driver = bspump.amqp.AMQPDriver(app)
	svc = app.get_service("bspump.PumpService")

	svc.add_pipelines(
		SamplePipeline1(app, 'SamplePipeline1', amqp_driver),
		SamplePipeline2(app, 'SamplePipeline2', amqp_driver),
	)

	app.run()
