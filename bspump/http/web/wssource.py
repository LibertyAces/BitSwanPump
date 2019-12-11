import asyncio
import logging

import aiohttp.web

from ...abc.source import Source


L = logging.getLogger(__name__)


class WebSocketSource(Source):


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.WebSockets = set()
		app.PubSub.subscribe("Application.exit!", self._on_exit)


	async def main(self):
		pass


	async def handler(self, request):
		ws = aiohttp.web.WebSocketResponse()
		await ws.prepare(request)

		self.WebSockets.add(ws)

		try:

			async for msg in ws:

				if msg.type == aiohttp.WSMsgType.BINARY or msg.type == aiohttp.WSMsgType.TEXT:
					await self.Pipeline.process(
						msg.data,
						context={
							'type': msg.type,
							'request': request
						}
					)

				elif msg.type == aiohttp.WSMsgType.ERROR:
					L.warning('WebSocket connection closed with exception {}'.format(ws.exception()))

				else:
					L.warning('WebSocket unknown/invalid message {}'.format(msg))

		finally:
			self.WebSockets.remove(ws)

		return ws


	async def _on_exit(self, event_name):
		# Close all existing web socket connections ...
		tasks = [ws.close() for ws in self.WebSockets]
		while len(tasks) > 0:
			done, tasks = await asyncio.wait(tasks)
