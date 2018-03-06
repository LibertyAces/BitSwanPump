#!/usr/bin/env python3
import asyncio
import asab
import bspump


class TCPDriver(asyncio.Protocol):

	def __init__(self, queue):
		self.queue = queue

	def connection_made(self, transport):
		peername = transport.get_extra_info('peername')
		print('Connection from {}'.format(peername))
		self.transport = transport

	def data_received(self, data):
		message = data.decode()
		print("data_received - 1", self.queue, self.queue.qsize(), message)
		self.queue.put_nowait(message)
		print("data_received - 2", self.queue, self.queue.qsize(), message)


class Source(bspump.Source):

	def __init__(self, app, pipeline, queue):
		super().__init__(app, pipeline)
		self.queue = queue


	async def get(self):
		event = await self.queue.get()
		return event


class Sink(bspump.Sink):

	def on_consume(self, data):
		print(">>>", data)


class SamplePipeline(bspump.Pipeline):


	def __init__(self, app, pipeline_id):
		self.queue = asyncio.Queue(maxsize=1000, loop=app.Loop)

		coro = app.Loop.create_server(lambda: TCPDriver(self.queue), '127.0.0.1', 8888)
		self.driver = app.Loop.run_until_complete(coro)

		super().__init__(app, pipeline_id)


	def construct(self, app):
		self.set_source(Source(app, self, self.queue))
		#self.append_processor(enrich)
		self.append_processor(Sink(app, self))



if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	pl = SamplePipeline(app, 'mypipeline')
	svc = app.get_service("bspump.PumpService")
	svc.add_pipeline(pl)

	app.run()
