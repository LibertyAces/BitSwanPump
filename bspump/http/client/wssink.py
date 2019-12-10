import logging
import asyncio
import aiohttp
from ...abc.sink import Sink


L = logging.getLogger(__name__)


class HTTPClientWebSocketSink(Sink):

	ConfigDefaults = {
		'url': 'https://localhost:8081/',
	}

	def __init__(self, app, pipeline, ssl=None, id=None, config=None):
		super().__init__(app, pipeline, id, config)

		self.Queue = asyncio.Queue()
		self.QueueMaxSize = 10
		self.SSL = ssl
		self.WebSocket = None
		self.Exiting = False

		self.Task = asyncio.ensure_future(
			self._task(self.Config['url']),
			loop=app.Loop
		)

		app.PubSub.subscribe("Application.exit!", self._on_exit)

		# We start throttled, till the connection to WS server is ready
		self.Pipeline.throttle(self, True)


	async def _task(self, url):
		async with aiohttp.ClientSession() as session:
			while not self.Exiting:
				try:
					async with session.ws_connect(
						url,
						ssl=self.SSL,
						heartbeat=30.0,
					) as ws:

						self.WebSocket = ws
						self.Pipeline.throttle(self, False)

						try:
							writer = asyncio.ensure_future(self._writer(ws), loop=self.Pipeline.Loop)
							reader = asyncio.ensure_future(self._reader(ws), loop=self.Pipeline.Loop)
							await asyncio.wait([writer, reader], return_when=asyncio.FIRST_COMPLETED)

						finally:
							self.WebSocket = None
							self.Pipeline.throttle(self, True)

						if not ws.closed:
							await ws.close()

						if not writer.done():
							writer.cancel()

						try:
							await writer
						except asyncio.CancelledError:
							pass

						if not reader.done():
							reader.cancel()

						try:
							await reader
						except asyncio.CancelledError:
							pass

						if self.Exiting:
							return

				except aiohttp.ClientError as e:
					L.warning("WebSocket error: {}".format(e))

				except Exception as e:
					L.warning("Error in websocket", exc_info=e)

				await asyncio.sleep(5)


	async def _writer(self, ws):
		while not ws.closed:
			event = await self.Queue.get()

			# Unthrottle if needed
			if self.Queue.qsize() == (self.QueueMaxSize - 1):
				self.Pipeline.throttle(self.Queue, True)

			if isinstance(event, (bytes, bytearray, memoryview)):
				await ws.send_bytes(event)
			else:
				await ws.send_str(event)


	async def _reader(self, ws):
		async for msg in ws:
			if msg.type == aiohttp.WSMsgType.ERROR:
				L.warning('WebSocket connection closed with exception {}'.format(ws.exception()))

			else:
				L.warning('WebSocket unknown/invalid message {}'.format(msg))

		if not self.Exiting:
			L.warning("Peer closed a connection")


	async def _on_exit(self, event_name):
		self.Exiting = True

		if self.WebSocket is not None:
			await self.WebSocket.close()

		if self.Task is not None:
			t = self.Task
			self.Task = None
			await t


	def process(self, context, event):
		self.Queue.put_nowait(event)
		if self.Queue.qsize() == self.QueueMaxSize:
			self.Pipeline.throttle(self.Queue, True)
