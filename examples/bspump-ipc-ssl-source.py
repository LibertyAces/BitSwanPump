#!/usr/bin/env python3
import os

import bspump
import bspump.ipc
import bspump.common


class EchoSink(bspump.Sink):

	def process(self, context, event):
		'''
		Send the event back to the client socket.
		'''
		print(event)
		sock = context['stream']
		sock.send(event.encode('utf-8'))
		sock.send(b'\n')


class EchoPipeline(bspump.Pipeline):

	'''
	To test this pipeline, use:
	socat STDIO TCP:127.0.0.1:8082
	'''

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		mydir = os.path.dirname(os.path.realpath(__file__))

		self.build(
			bspump.ipc.StreamServerSource(app, self, config={
				'address': ':: 8082',
				'cert': os.path.join(mydir, './ssl/cert.pem'),
				'key': os.path.join(mydir, './ssl/key.pem'),
			}),
			EchoSink(app, self)
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()
	svc = app.get_service("bspump.PumpService")
	svc.add_pipeline(EchoPipeline(app, "EchoPipeline"))
	app.run()
