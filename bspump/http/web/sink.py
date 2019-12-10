import logging
import queue

import aiohttp.web
import itertools

from ...abc.sink import Sink

#

L = logging.getLogger(__name__)

#


class WebServiceStreamResponse(aiohttp.web.StreamResponse):

	Counter = itertools.count(1, 1)


	def __init__(self, sink):
		super().__init__()
		self.Id = '{}.{}#{}'.format(sink.Pipeline.Id, sink.Id, next(self.Counter))
		self.Sink = sink
		self.Queue = queue.Queue()

	# Context Manager

	async def __aenter__(self):
		self.Sink.Responses[self.Id] = self


	async def __aexit__(self, exc_type, exc, tb):
		# Remove myself from a sink
		del self.Sink.Responses[self.Id]
		self.Sink = None

		await self.flush_events()
		await self.write_eof()

	# Queue management

	def put_event(self, event):
		self.Queue.put_nowait(event)


	async def flush_events(self):
		while not self.Queue.empty():
			event = self.Queue.get_nowait()
			await self.write(event)




class WebServiceSink(Sink):

	'''
Example of use:

	async def endpoint(self, request):
		response = await self.WebServiceSink.response(request)
		async with response:
			data = await request.read()
			await self.WebServiceSource.put({self.WebServiceSink.CONTEXT_RESPONSE_ID:response.Id}, data, request)
		return response

Note: Source doesn't necessarily needs to originate at WebServiceSink, it could be e.g. any triggered source.

	'''


	CONTEXT_RESPONSE_ID = "webservicesink.response_id"


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		self.Responses = {}
		app.PubSub.subscribe("Application.tick!", self.on_tick)


	def process(self, context, event):
		response_id = context.get(self.CONTEXT_RESPONSE_ID)
		if response_id is None:
			L.warning("Missing CONTEXT_RESPONSE_ID entry in the context")
			return

		response = self.Responses[response_id]
		if response_id is None:
			L.warning("Cannot locate web response '{}'".format(response_id))
			return

		response.put_event(event)


	async def response(self, request):
		response = WebServiceStreamResponse(self)
		await response.prepare(request)
		return response


	async def on_tick(self, event_name):
		for response in self.Responses:
			await response.flush_events()
