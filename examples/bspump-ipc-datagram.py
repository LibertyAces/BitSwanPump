#!/usr/bin/env python3
import bspump
import bspump.common
import bspump.ipc
import bspump.socket


class StreamSinkPipeline(bspump.Pipeline):
	"""
	To test this pipeline, use:
	socat STDIO TCP:127.0.0.1:8082
	"""

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.socket.TCPSource(app, self, config={'address': '127.0.0.1:8082'}),
			bspump.common.PPrintProcessor(app, self),
			# bspump.ipc.DatagramSink(app, self, config={"address": "/tmp/bspump-ipc-datagram.sock"}),
			bspump.ipc.DatagramSink(app, self, config={'address': '127.0.0.1:8083'}),
		)


class StreamSourcePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			# bspump.ipc.DatagramSource(app, self, config={"address": "/tmp/bspump-ipc-datagram.sock"}),
			bspump.ipc.DatagramSource(app, self, config={'address': '127.0.0.1:8083'}),
			bspump.common.PPrintSink(app, self),
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()
	svc = app.get_service("bspump.PumpService")
	svc.add_pipeline(StreamSourcePipeline(app, "StreamSourcePipeline"))
	svc.add_pipeline(StreamSinkPipeline(app, "StreamSinkPipeline"))
	app.run()
