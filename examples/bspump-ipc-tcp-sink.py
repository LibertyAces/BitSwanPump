#!/usr/bin/env python3
import asyncio

import bspump
import bspump.common
import bspump.ipc


class PeriodicSource(bspump.Source):

	async def main(self):
		counter = 1
		while True:
			await asyncio.sleep(1)
			await self.Pipeline.ready()
			await self.Pipeline.process('Tick {}\n'.format(counter).encode('ascii'))
			counter += 1


class StreamSinkPipeline(bspump.Pipeline):
	"""
	To test this pipeline, use:
	socat TCP-LISTEN:8083,reuseaddr STDIO
	"""

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			PeriodicSource(app, self),
			bspump.common.PPrintProcessor(app, self),
			# bspump.ipc.StreamSink(app, self, config={"address": "/tmp/bspump-ipc-stream.sock"}),
			bspump.ipc.StreamSink(app, self, config={'address': '127.0.0.1 8083'}),
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()
	svc = app.get_service("bspump.PumpService")
	svc.add_pipeline(StreamSinkPipeline(app, "StreamSinkPipeline"))
	app.run()
