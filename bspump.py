#!/usr/bin/env python3
import asyncio
import asab
import bspump


class TCPStreamProtocol(asyncio.Protocol):

	def __init__(self, source):
		self._source = source

	def connection_made(self, transport):
		peername = transport.get_extra_info('peername')
		print('Connection from {}'.format(peername))
		self.transport = transport

	def data_received(self, data):
		message = data.decode()
		self._source.process(data)


class TCPStreamSource(bspump.Source):

	async def start(self):
		self.server = await app.Loop.create_server(lambda: TCPStreamProtocol(self), '127.0.0.1', 8888)


class PrintSink(bspump.Sink):

	def process(self, data):
		print(">>>", data)


class SamplePipeline(bspump.Pipeline):


	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.set_source(TCPStreamSource(app, self))
		#self.append_processor(enrich)
		self.append_processor(PrintSink(app, self))



if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	pl = SamplePipeline(app, 'mypipeline')
	svc = app.get_service("bspump.PumpService")
	svc.add_pipeline(pl)

	app.run()
