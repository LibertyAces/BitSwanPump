#!/usr/bin/env python3
import asyncio
import asab
import bspump
from bspump.amqp import AMQPDriver
from bspump.amqp import AMQPSource



class DummySource(Source):
	def __init__(self, app, pipeline):
		super().__init__(app, pipeline)

	async def start(self):
		self.process({
			"@timestamp": "blabla",
		})

class PrintSink(bspump.Sink):
	def process(self, data):
		print(">>>", data)


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.driver = AMQPDriver(app)
		self.set_source(AMQPSource(app, self, self.driver))
		self.append_processor(PrintSink(app, self))


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	pl = SamplePipeline(app, 'mypipeline')
	svc = app.get_service("bspump.PumpService")
	svc.add_pipeline(pl)

	app.run()