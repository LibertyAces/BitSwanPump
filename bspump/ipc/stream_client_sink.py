import asyncio
import logging
import socket
import re

from ..abc.sink import Sink

from .stream import Stream, TLSStream
from .utils import parse_address

#

L = logging.getLogger(__name__)

#


class StreamClientSink(Sink):

	ConfigDefaults = {
		'address': '127.0.0.1 8888',  # IPv4, IPv6 or unix socket path
		'outbound_queue_max_size': 100,  # Maximum size of the output queue before throttling
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.OutboundQueue = asyncio.Queue()

		# Throttle till we are connected
		self.Pipeline.throttle(self, enable=True)

		# Maximum size for the queue
		self.OutboundQueueMaxSize = int(self.Config['outbound_queue_max_size'])
		assert (self.OutboundQueueMaxSize >= 1)

		self.Task = None

		self.Pipeline.PubSub.subscribe("bspump.pipeline.start!", self._open_connection)
		self.Pipeline.PubSub.subscribe("bspump.pipeline.stop!", self._close_connection)
		app.PubSub.subscribe("Application.tick!", self._on_tick)


	async def _open_connection(self, message, pipeline):
		# Connection is established
		if self.Task is not None:
			await self._close_connection(message, pipeline)

		self.Task = self.Pipeline.Loop.create_task(
			self._client_connected_task()
		)


	async def _close_connection(self, message, pipeline):
		self.Pipeline.throttle(self, enable=True)
		if self.Task is not None:
			self.Task.cancel()
			self.Task = None


	def _on_tick(self, event_name):
		# Unthrottle the queue if needed
		if self.OutboundQueue in self.Pipeline.get_throttles() and self.OutboundQueue.qsize() < self.OutboundQueueMaxSize:
			self.Pipeline.throttle(self.OutboundQueue, False)

		if self.Task is not None and self.Task.done():
			# We should be connected but we are not
			# Let's do a bit of clean-up and commence reconnection

			try:
				self.Task.result()
			except Exception:
				L.exception("Error when handling client socket")


			self.Task = self.Pipeline.Loop.create_task(
				self._client_connected_task()
			)


	async def _client_connected_task(self):
		loop = self.Pipeline.Loop

		address = self.Config['address']
		addr_family, addr = parse_address(address)

		if addr_family == socket.AF_UNIX:
			# TODO: This, it is a simple connect() to AF_UNIX socket
			raise NotImplementedError()

		addrinfo = await loop.getaddrinfo(addr[0], addr[1], family=socket.AF_UNSPEC, type=socket.SOCK_STREAM)

		# Connect to the first usable addrinfo
		client_sock = None
		connection_exception = ''
		for family, socktype, proto, canonname, sockaddr in addrinfo:
			client_sock = socket.socket(family, socktype, proto)
			client_sock.setblocking(False)
			try:
				await loop.sock_connect(client_sock, sockaddr)
				break
			except Exception as e:
				connection_exception = e
				client_sock = None
				continue

		if client_sock is None:
			L.warning("Connection to '{}' failed: {}".format(addr, connection_exception))
			return

		# TODO: Support also TLSStream ...
		stream = Stream(self.Pipeline.Loop, client_sock, outbound_queue=self.OutboundQueue)

		outbound = loop.create_task(stream.outbound())
		inbound = loop.create_task(self._client_inbound_task(client_sock))

		self.Pipeline.throttle(self, enable=False)
		try:
			done, active = await asyncio.wait(
				{outbound, inbound},
				return_when=asyncio.FIRST_COMPLETED
			)

		except asyncio.CancelledError:
			active = {outbound, inbound}
			done = {}

		finally:
			self.Pipeline.throttle(self, enable=True)

		# Cancel remaining active tasks
		for t in active:
			# TODO: There could be outstanding data in the outbound queue
			#       Consider flushing them
			t.cancel()

		# Collect results from completed tasks
		for t in done:
			try:
				await t
			except asyncio.CancelledError:
				pass
			except Exception:
				L.exception("Error when handling client socket")

		# Close the stream
		await stream.close()


	async def _client_inbound_task(self, client_sock):
		while True:
			data = await self.Pipeline.Loop.sock_recv(client_sock, 4096)
			if len(data) == 0:
				# Client closed the connection
				return

			# Incoming data are discarted ...


	def process(self, context, event):
		self.OutboundQueue.put_nowait(event)

		if self.OutboundQueue.qsize() == self.OutboundQueueMaxSize:
			self.Pipeline.throttle(self.OutboundQueue, True)
